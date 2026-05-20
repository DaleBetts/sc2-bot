from __future__ import annotations

import random

from sc2.bot_ai import BotAI
from sc2.data import Race, Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2

from bot.logger import GameLogger

_CHEESE_DT = "dt_rush"
_CHEESE_4GATE = "four_gate"

_WORKER_TYPES = {UnitTypeId.DRONE, UnitTypeId.SCV, UnitTypeId.PROBE}

_ARMY_TYPES = {
    UnitTypeId.STALKER,
    UnitTypeId.ZEALOT,
    UnitTypeId.COLOSSUS,
    UnitTypeId.IMMORTAL,
    UnitTypeId.ARCHON,
    UnitTypeId.DARKTEMPLAR,
}

_ZERG_ARMY_TYPES = _ARMY_TYPES | {
    UnitTypeId.SENTRY,
    UnitTypeId.HIGHTEMPLAR,
    UnitTypeId.DISRUPTOR,
    UnitTypeId.ORACLE,
    UnitTypeId.VOIDRAY,
}


class CompetitiveBot(BotAI):
    NAME: str = "GrubbyBot"
    RACE: Race = Race.Protoss

    async def on_start(self) -> None:
        self.client.game_step = 2
        # 25% DT rush, 25% 4-gate, 50% standard macro
        self._cheese_type: str | None = random.choice([
            _CHEESE_DT, _CHEESE_4GATE, None, None,
        ])
        self._scout_sent: bool = False
        self._last_log_minute: int = -1
        self._logger = GameLogger()
        self._logger.log(
            "game_start",
            game_time=0.0,
            opponent_id=getattr(self, "opponent_id", "unknown"),
            opponent_race=self.enemy_race.name,
            map_name=self.game_info.map_name,
            strategy=self._cheese_type or "standard_macro",
        )
        # Burnysc2's ability data lags behind SC2 game patches.
        # Any unknown ability ID causes unit.orders to KeyError throughout the library.
        # Stub them out so they parse cleanly without crashing.
        if self.game_data.abilities:
            _stub = next(iter(self.game_data.abilities.values()))
            for _unknown_id in [4446]:
                if _unknown_id not in self.game_data.abilities:
                    self.game_data.abilities[_unknown_id] = _stub

    @property
    def _vs_zerg(self) -> bool:
        return self.enemy_race == Race.Zerg

    @property
    def _cheese_active(self) -> bool:
        # Cheese window: first 8 minutes. After that, fall back to standard macro.
        return self._cheese_type is not None and self.time < 480

    async def on_step(self, iteration: int) -> None:
        if iteration == 0:
            await self.chat_send("gl hf - En Taro Artanis!")
        await self.distribute_workers()
        self._maybe_log_periodic()
        await self._scout()
        await self._build_pylons()
        await self._train_probes()
        await self._expand()
        await self._build_structures()
        await self._build_cannons()
        await self._morph_warpgates()
        await self._produce_army()
        await self._research_upgrades()
        await self._attack()
        await self._stalker_blink_micro()
        await self._stalker_kite()
        if self._cheese_active and self._cheese_type == _CHEESE_DT:
            await self._dt_harass()
        if self._vs_zerg and not self._cheese_active:
            await self._zerg_micro()
            await self._anti_creep_overlord()

    # ── Periodic logging ──────────────────────────────────────────────────────

    def _maybe_log_periodic(self) -> None:
        minute = int(self.time // 60)
        if minute <= self._last_log_minute:
            return
        self._last_log_minute = minute
        army = self.units.filter(lambda u: u.type_id in _ARMY_TYPES)
        self._logger.log(
            "periodic",
            game_time=self.time,
            minute=minute,
            workers=self.workers.amount,
            bases=self.townhalls.amount,
            supply_used=self.supply_used,
            supply_cap=self.supply_cap,
            supply_left=self.supply_left,
            minerals=self.minerals,
            vespene=self.vespene,
            army_count=army.amount,
            cheese_active=self._cheese_active,
        )

    # ── Scouting ──────────────────────────────────────────────────────────────

    async def _scout(self) -> None:
        if self._scout_sent or self.workers.amount < 14:
            return
        probe = self.workers.closest_to(self.start_location)
        if probe:
            probe.move(self.enemy_start_locations[0])
            self._scout_sent = True

    # ── Supply ───────────────────────────────────────────────────────────────

    async def _build_pylons(self) -> None:
        if (
            self.supply_cap < 200
            and self.supply_left < 16
            and self.already_pending(UnitTypeId.PYLON) < 6
            and self.can_afford(UnitTypeId.PYLON)
            and self.townhalls
        ):
            pos = self.townhalls.random.position.towards(self.game_info.map_center, 5)
            placement = await self.find_placement(UnitTypeId.PYLON, pos)
            if placement:
                worker = self.select_build_worker(placement)
                if worker:
                    worker.build(UnitTypeId.PYLON, placement)

    # ── Workers ───────────────────────────────────────────────────────────────

    async def _train_probes(self) -> None:
        worker_cap = min(60, max(40, self.townhalls.amount * 22))
        if self._cheese_active:
            # Cut probe production during all-ins so minerals flow to units
            # For DT rush, only cut workers once the Dark Shrine is actually ready and producing DTs
            dark_shrine_done = bool(self.structures(UnitTypeId.DARKSHRINE).ready)
            if self._cheese_type == _CHEESE_DT and not dark_shrine_done:
                worker_cap = 22
            elif self._cheese_type == _CHEESE_DT:
                worker_cap = 20
            else:
                worker_cap = 18
        for nexus in self.townhalls.ready.idle:
            if self.workers.amount < worker_cap and self.can_afford(UnitTypeId.PROBE) and self.supply_left > 0:
                nexus.train(UnitTypeId.PROBE)

    # ── Structures ───────────────────────────────────────────────────────────

    async def _build_structures(self) -> None:
        if not self.townhalls or not self.structures(UnitTypeId.PYLON).ready:
            return

        pylon = self.structures(UnitTypeId.PYLON).ready.closest_to(self.start_location)

        if (
            not self.structures(UnitTypeId.GATEWAY)
            and not self.already_pending(UnitTypeId.GATEWAY)
            and self.supply_used >= 14
            and self.can_afford(UnitTypeId.GATEWAY)
        ):
            await self._place_near(UnitTypeId.GATEWAY, pylon.position)

        if self.structures(UnitTypeId.GATEWAY) or self.already_pending(UnitTypeId.GATEWAY):
            await self._build_assimilators()

        if (
            self.structures(UnitTypeId.GATEWAY).ready
            and not self.structures(UnitTypeId.CYBERNETICSCORE)
            and not self.already_pending(UnitTypeId.CYBERNETICSCORE)
            and self.can_afford(UnitTypeId.CYBERNETICSCORE)
        ):
            await self._place_near(UnitTypeId.CYBERNETICSCORE, pylon.position)

        if not self.structures(UnitTypeId.CYBERNETICSCORE).ready:
            return

        # 4-gate: rush to 4 gateways; DT rush: 2 gateways is enough; standard: scale with bases
        if self._cheese_active and self._cheese_type == _CHEESE_4GATE:
            target_gw = 4
        else:
            target_gw = min(8, 3 + self.townhalls.amount)

        gw_total = (
            self.structures(UnitTypeId.GATEWAY).amount
            + self.structures(UnitTypeId.WARPGATE).amount
            + self.already_pending(UnitTypeId.GATEWAY)
        )
        # Also build extra gateways to spend excess minerals when not cheese
        effective_target = target_gw
        if not self._cheese_active and self.minerals > 400:
            effective_target = min(16, gw_total + 2)
        if not self._cheese_active and self.supply_used >= 190 and self.minerals > 400:
            effective_target = min(24, gw_total + 4)
        if gw_total < effective_target and self.can_afford(UnitTypeId.GATEWAY):
            await self._place_near(UnitTypeId.GATEWAY, pylon.position)

        # Skip Robotics during cheese — every mineral goes to gates/units
        if not self._cheese_active:
            if (
                not self.structures(UnitTypeId.ROBOTICSFACILITY)
                and not self.already_pending(UnitTypeId.ROBOTICSFACILITY)
                and self.can_afford(UnitTypeId.ROBOTICSFACILITY)
            ):
                await self._place_near(UnitTypeId.ROBOTICSFACILITY, pylon.position)

            if (
                self.structures(UnitTypeId.ROBOTICSFACILITY).ready
                and not self.structures(UnitTypeId.ROBOTICSBAY)
                and not self.already_pending(UnitTypeId.ROBOTICSBAY)
                and self.can_afford(UnitTypeId.ROBOTICSBAY)
            ):
                await self._place_near(UnitTypeId.ROBOTICSBAY, pylon.position)

        # Twilight Council:
        #   DT rush — build immediately after Cyber Core (no base requirement)
        #   4-gate  — skip entirely, all money to gates
        #   standard — requires 2 bases
        dt_rush_active = self._cheese_active and self._cheese_type == _CHEESE_DT
        four_gate_active = self._cheese_active and self._cheese_type == _CHEESE_4GATE
        tc_base_req = 1 if dt_rush_active else 2
        if (
            not four_gate_active
            and self.townhalls.amount >= tc_base_req
            and not self.structures(UnitTypeId.TWILIGHTCOUNCIL)
            and not self.already_pending(UnitTypeId.TWILIGHTCOUNCIL)
            and self.can_afford(UnitTypeId.TWILIGHTCOUNCIL)
        ):
            await self._place_near(UnitTypeId.TWILIGHTCOUNCIL, pylon.position)

        # Dark Shrine — DT rush only
        if dt_rush_active and self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready:
            if (
                not self.structures(UnitTypeId.DARKSHRINE)
                and not self.already_pending(UnitTypeId.DARKSHRINE)
                and self.can_afford(UnitTypeId.DARKSHRINE)
            ):
                await self._place_near(UnitTypeId.DARKSHRINE, pylon.position)

        # Skip Forge and Zerg-specific structures during cheese all-in
        if not self._cheese_active:
            forge_threshold = 1 if self._vs_zerg else 2
            if (
                self.townhalls.amount >= forge_threshold
                and not self.structures(UnitTypeId.FORGE)
                and not self.already_pending(UnitTypeId.FORGE)
                and self.can_afford(UnitTypeId.FORGE)
            ):
                await self._place_near(UnitTypeId.FORGE, pylon.position)

            if self._vs_zerg:
                await self._build_zerg_structures(pylon.position)

    async def _build_zerg_structures(self, pylon_pos: Point2) -> None:
        if (
            not self.structures(UnitTypeId.STARGATE)
            and not self.already_pending(UnitTypeId.STARGATE)
            and self.can_afford(UnitTypeId.STARGATE)
        ):
            await self._place_near(UnitTypeId.STARGATE, pylon_pos)

        if self.townhalls.amount >= 2:
            natural = self.townhalls.furthest_to(self.start_location)
            battery_count = (
                self.structures(UnitTypeId.SHIELDBATTERY).closer_than(15, natural).amount
                + self.already_pending(UnitTypeId.SHIELDBATTERY)
            )
            if battery_count < 2 and self.can_afford(UnitTypeId.SHIELDBATTERY):
                pos = natural.position.towards(self.start_location, 5)
                placement = await self.find_placement(UnitTypeId.SHIELDBATTERY, pos, placement_step=2)
                if placement:
                    worker = self.select_build_worker(placement)
                    if worker:
                        worker.build(UnitTypeId.SHIELDBATTERY, placement)

        if (
            self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
            and not self.structures(UnitTypeId.TEMPLARARCHIVE)
            and not self.already_pending(UnitTypeId.TEMPLARARCHIVE)
            and self.can_afford(UnitTypeId.TEMPLARARCHIVE)
        ):
            await self._place_near(UnitTypeId.TEMPLARARCHIVE, pylon_pos)

    async def _build_cannons(self) -> None:
        if not self.structures(UnitTypeId.FORGE).ready or self.townhalls.amount < 2:
            return
        natural = self.townhalls.furthest_to(self.start_location)
        cannon_count = (
            self.structures(UnitTypeId.PHOTONCANNON).closer_than(15, natural).amount
            + self.already_pending(UnitTypeId.PHOTONCANNON)
        )
        if cannon_count < 2 and self.can_afford(UnitTypeId.PHOTONCANNON):
            pos = natural.position.towards(self.start_location, 4)
            placement = await self.find_placement(UnitTypeId.PHOTONCANNON, pos, placement_step=2)
            if placement:
                worker = self.select_build_worker(placement)
                if worker:
                    worker.build(UnitTypeId.PHOTONCANNON, placement)

    async def _build_assimilators(self) -> None:
        for nexus in self.townhalls.ready:
            if self.gas_buildings.closer_than(10, nexus).amount >= 2:
                continue
            for geyser in self.vespene_geyser.closer_than(10, nexus):
                if not self.gas_buildings.closer_than(1, geyser) and self.can_afford(UnitTypeId.ASSIMILATOR):
                    worker = self.select_build_worker(geyser.position)
                    if worker:
                        worker.build(UnitTypeId.ASSIMILATOR, geyser)
                    break

    async def _place_near(self, building: UnitTypeId, near: Point2) -> None:
        pos = near.towards(self.game_info.map_center, 6)
        placement = await self.find_placement(building, pos, placement_step=2)
        if placement:
            worker = self.select_build_worker(placement)
            if worker:
                worker.build(building, placement)

    # ── Warp Gate morph ──────────────────────────────────────────────────────

    async def _morph_warpgates(self) -> None:
        if self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 1:
            for gw in self.structures(UnitTypeId.GATEWAY).ready.idle:
                gw(AbilityId.MORPH_WARPGATE)

    # ── Army production ──────────────────────────────────────────────────────

    async def _produce_army(self) -> None:
        await self._gateway_units()
        if not self._cheese_active:
            await self._robo_units()
            if self._vs_zerg and self.structures(UnitTypeId.STARGATE).ready:
                await self._stargate_units()

    async def _gateway_units(self) -> None:
        pylons = self.structures(UnitTypeId.PYLON).ready
        if not pylons:
            return
        if self._cheese_active and self._cheese_type == _CHEESE_DT:
            spawn_near = pylons.closest_to(self.start_location).position.towards(self.game_info.map_center, 8)
        else:
            spawn_near = pylons.closest_to(self.start_location).position.towards(self.start_location, 3)

        dark_shrine_ready = bool(self.structures(UnitTypeId.DARKSHRINE).ready)
        sentry_count = self.units(UnitTypeId.SENTRY).amount + self.already_pending(UnitTypeId.SENTRY)
        ht_count = self.units(UnitTypeId.HIGHTEMPLAR).amount + self.already_pending(UnitTypeId.HIGHTEMPLAR)
        archives_ready = bool(self.structures(UnitTypeId.TEMPLARARCHIVE).ready)

        for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
            if self.supply_left <= 0:
                break
            abilities = await self.get_available_abilities(warpgate)

            # DT rush: DTs first once Dark Shrine is ready
            if (
                self._cheese_active
                and self._cheese_type == _CHEESE_DT
                and dark_shrine_ready
                and AbilityId.WARPGATETRAIN_DARKTEMPLAR in abilities
                and self.can_afford(UnitTypeId.DARKTEMPLAR)
            ):
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_DARKTEMPLAR, spawn_near, placement_step=2)
                if placement:
                    warpgate(AbilityId.WARPGATETRAIN_DARKTEMPLAR, placement)
            elif (
                not self._cheese_active
                and self._vs_zerg
                and archives_ready
                and ht_count < 4
                and AbilityId.WARPGATETRAIN_HIGHTEMPLAR in abilities
                and self.can_afford(UnitTypeId.HIGHTEMPLAR)
            ):
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_HIGHTEMPLAR, spawn_near, placement_step=2)
                if placement:
                    warpgate(AbilityId.WARPGATETRAIN_HIGHTEMPLAR, placement)
            elif AbilityId.WARPGATETRAIN_STALKER in abilities and self.can_afford(UnitTypeId.STALKER):
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, spawn_near, placement_step=2)
                if placement:
                    warpgate(AbilityId.WARPGATETRAIN_STALKER, placement)
            elif (
                not self._cheese_active
                and self._vs_zerg
                and sentry_count < 3
                and AbilityId.WARPGATETRAIN_SENTRY in abilities
                and self.can_afford(UnitTypeId.SENTRY)
            ):
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_SENTRY, spawn_near, placement_step=2)
                if placement:
                    warpgate(AbilityId.WARPGATETRAIN_SENTRY, placement)
            elif AbilityId.WARPGATETRAIN_ZEALOT in abilities and self.can_afford(UnitTypeId.ZEALOT):
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, spawn_near, placement_step=2)
                if placement:
                    warpgate(AbilityId.WARPGATETRAIN_ZEALOT, placement)

        for gw in self.structures(UnitTypeId.GATEWAY).ready.idle:
            if self.supply_left <= 0:
                break
            if (
                self._cheese_active
                and self._cheese_type == _CHEESE_DT
                and dark_shrine_ready
                and self.can_afford(UnitTypeId.DARKTEMPLAR)
            ):
                gw.train(UnitTypeId.DARKTEMPLAR)
            elif not self._cheese_active and self._vs_zerg and archives_ready and ht_count < 4 and self.can_afford(UnitTypeId.HIGHTEMPLAR):
                gw.train(UnitTypeId.HIGHTEMPLAR)
                ht_count += 1
            elif self.can_afford(UnitTypeId.STALKER):
                gw.train(UnitTypeId.STALKER)
            elif not self._cheese_active and self._vs_zerg and sentry_count < 3 and self.can_afford(UnitTypeId.SENTRY):
                gw.train(UnitTypeId.SENTRY)
                sentry_count += 1
            elif self.can_afford(UnitTypeId.ZEALOT):
                gw.train(UnitTypeId.ZEALOT)

    async def _robo_units(self) -> None:
        colossus_cap = 6 if self._vs_zerg else 4

        for robo in self.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle:
            if self.supply_left <= 0:
                break
            colossus_count = self.units(UnitTypeId.COLOSSUS).amount + self.already_pending(UnitTypeId.COLOSSUS)
            disruptor_count = self.units(UnitTypeId.DISRUPTOR).amount + self.already_pending(UnitTypeId.DISRUPTOR)
            robo_bay_ready = bool(self.structures(UnitTypeId.ROBOTICSBAY).ready)

            if robo_bay_ready and colossus_count < colossus_cap and self.can_afford(UnitTypeId.COLOSSUS):
                robo.train(UnitTypeId.COLOSSUS)
            elif self._vs_zerg and robo_bay_ready and disruptor_count < 3 and self.can_afford(UnitTypeId.DISRUPTOR):
                robo.train(UnitTypeId.DISRUPTOR)
            elif self.can_afford(UnitTypeId.IMMORTAL):
                robo.train(UnitTypeId.IMMORTAL)

    async def _stargate_units(self) -> None:
        oracle_count = self.units(UnitTypeId.ORACLE).amount + self.already_pending(UnitTypeId.ORACLE)
        voidray_count = self.units(UnitTypeId.VOIDRAY).amount + self.already_pending(UnitTypeId.VOIDRAY)

        for sg in self.structures(UnitTypeId.STARGATE).ready.idle:
            if self.supply_left <= 0:
                break
            if oracle_count < 2 and self.can_afford(UnitTypeId.ORACLE):
                sg.train(UnitTypeId.ORACLE)
                oracle_count += 1
            elif voidray_count < 3 and self.can_afford(UnitTypeId.VOIDRAY):
                sg.train(UnitTypeId.VOIDRAY)
                voidray_count += 1

    # ── Upgrades ─────────────────────────────────────────────────────────────

    async def _research_upgrades(self) -> None:
        if (
            self.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0
            and self.can_afford(UpgradeId.WARPGATERESEARCH)
        ):
            self.structures(UnitTypeId.CYBERNETICSCORE).first.research(UpgradeId.WARPGATERESEARCH)

        if (
            self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
            and self.already_pending_upgrade(UpgradeId.BLINKTECH) == 0
            and self.can_afford(UpgradeId.BLINKTECH)
        ):
            self.structures(UnitTypeId.TWILIGHTCOUNCIL).first.research(UpgradeId.BLINKTECH)

        if (
            self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
            and self.already_pending_upgrade(UpgradeId.CHARGE) == 0
            and self.already_pending_upgrade(UpgradeId.BLINKTECH) == 1
            and self.can_afford(UpgradeId.CHARGE)
        ):
            self.structures(UnitTypeId.TWILIGHTCOUNCIL).first.research(UpgradeId.CHARGE)

        if not self._cheese_active:
            if (
                self.structures(UnitTypeId.ROBOTICSBAY).ready
                and self.already_pending_upgrade(UpgradeId.EXTENDEDTHERMALLANCE) == 0
                and self.can_afford(UpgradeId.EXTENDEDTHERMALLANCE)
            ):
                self.structures(UnitTypeId.ROBOTICSBAY).first.research(UpgradeId.EXTENDEDTHERMALLANCE)

            if self.structures(UnitTypeId.FORGE).ready:
                if (
                    self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1) == 0
                    and self.can_afford(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1)
                ):
                    self.structures(UnitTypeId.FORGE).first.research(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1)
                elif (
                    self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1) == 1
                    and self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2) == 0
                    and self.can_afford(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2)
                ):
                    self.structures(UnitTypeId.FORGE).first.research(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2)
                elif (
                    self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2) == 1
                    and self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3) == 0
                    and self.can_afford(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3)
                ):
                    self.structures(UnitTypeId.FORGE).first.research(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3)

            if (
                self._vs_zerg
                and self.structures(UnitTypeId.TEMPLARARCHIVE).ready
                and self.already_pending_upgrade(UpgradeId.PSISTORMTECH) == 0
                and self.can_afford(UpgradeId.PSISTORMTECH)
            ):
                self.structures(UnitTypeId.TEMPLARARCHIVE).first.research(UpgradeId.PSISTORMTECH)

    # ── Expansion ─────────────────────────────────────────────────────────────

    async def _expand(self) -> None:
        if self._cheese_active:
            return  # No expansion during all-in
        target = 1 + (self.workers.amount // 16)
        # Require some defensive infrastructure before taking a second base
        gw_count = (
            self.structures(UnitTypeId.GATEWAY).amount
            + self.structures(UnitTypeId.WARPGATE).amount
        )
        army_types = _ZERG_ARMY_TYPES if self._vs_zerg else _ARMY_TYPES
        army_size = self.units.filter(lambda u: u.type_id in army_types).amount
        has_defense = (
            self.townhalls.amount >= 2
            or (gw_count >= 1 and army_size >= 2)
            or (gw_count >= 2 and army_size >= 1)
            or army_size >= 4
            or self.time > 420
            or self.structures(UnitTypeId.FORGE).ready
            or self.already_pending(UnitTypeId.FORGE)
            or self.structures(UnitTypeId.SHIELDBATTERY).amount > 0
            or self.already_pending(UnitTypeId.SHIELDBATTERY)
        )
        if (
            self.townhalls.amount < target
            and has_defense
            and not self.already_pending(UnitTypeId.NEXUS)
            and self.can_afford(UnitTypeId.NEXUS)
        ):
            await self.expand_now()

    # ── Attack ───────────────────────────────────────────────────────────────

    async def _attack(self) -> None:
        army_types = _ZERG_ARMY_TYPES if self._vs_zerg else _ARMY_TYPES
        # DTs handled by _dt_harass — keep them out of the main army rally logic
        if self._cheese_active and self._cheese_type == _CHEESE_DT:
            army_types = army_types - {UnitTypeId.DARKTEMPLAR}
        army = self.units.filter(lambda u: u.type_id in army_types)

        if not army:
            return

        near_base = self.enemy_units.closer_than(25, self.start_location)
        if near_base:
            for unit in army:
                unit.attack(near_base.closest_to(unit))
            # Pull up to 4 workers to defend if army is small
            if army.amount < 4:
                for worker in self.workers.closer_than(15, self.start_location)[:4]:
                    worker.attack(near_base.closest_to(worker))
            return
        enemy_near_workers = self.enemy_units.closer_than(15, self.start_location)
        if enemy_near_workers and army.amount > 0:
            for unit in army:
                unit.attack(enemy_near_workers.closest_to(unit))
            return

        # 4-gate attacks with 8 units; standard attacks with 4 units to apply early pressure; force attack after 10 min
        if self._cheese_active and self._cheese_type == _CHEESE_4GATE:
            army_threshold = 6
        elif not self._cheese_active and self.time > 600:
            army_threshold = 4
        else:
            army_threshold = 6
        if not self.townhalls:
            return
        rally = self.townhalls.closest_to(self.start_location).position.towards(self.game_info.map_center, 15)
        if army.amount < army_threshold:
            for unit in army.idle:
                unit.move(rally)
            return

        target = (
            self.enemy_structures.closest_to(self.start_location).position
            if self.enemy_structures
            else self.enemy_start_locations[0]
        )
        for unit in army.idle:
            unit.attack(target)

    # ── Stalker Blink micro ───────────────────────────────────────────────────

    async def _stalker_blink_micro(self) -> None:
        if self.already_pending_upgrade(UpgradeId.BLINKTECH) < 1:
            return

        for stalker in self.units(UnitTypeId.STALKER):
            total_hp = stalker.health + stalker.shield
            total_max = stalker.health_max + stalker.shield_max
            if total_max == 0:
                continue
            if total_hp / total_max < 0.3:
                abilities = await self.get_available_abilities(stalker)
                if AbilityId.EFFECT_BLINK_STALKER in abilities:
                    retreat = stalker.position.towards(self.start_location, 8)
                    stalker(AbilityId.EFFECT_BLINK_STALKER, retreat)

    # ── Stalker stutter-step kiting ──────────────────────────────────────────

    async def _stalker_kite(self) -> None:
        for stalker in self.units(UnitTypeId.STALKER):
            # Let blink micro handle critically wounded Stalkers
            total_hp = stalker.health + stalker.shield
            total_max = stalker.health_max + stalker.shield_max
            if total_max > 0 and total_hp / total_max < 0.3:
                continue

            # Only kite when enemies are close enough to matter (just beyond attack range)
            nearby_enemies = self.enemy_units.closer_than(8, stalker)
            if not nearby_enemies:
                continue

            if stalker.weapon_cooldown == 0:
                # Weapon ready — fire at the nearest threat
                stalker.attack(nearby_enemies.closest_to(stalker))
            else:
                # Weapon cooling — back away from the enemy mass to gain separation
                retreat = stalker.position.towards(self.start_location, 3)
                stalker.move(retreat)

    # ── DT Rush micro ────────────────────────────────────────────────────────

    async def _dt_harass(self) -> None:
        # Send each DT directly to enemy workers; if workers unknown, go to their base
        for dt in self.units(UnitTypeId.DARKTEMPLAR).idle:
            enemy_workers = self.enemy_units.filter(lambda u: u.type_id in _WORKER_TYPES)
            if enemy_workers:
                dt.attack(enemy_workers.closest_to(dt))
            elif self.enemy_structures:
                dt.attack(self.enemy_structures.closest_to(dt))
            elif self.enemy_start_locations:
                dt.move(self.enemy_start_locations[0])

    # ── Zerg-specific behaviors ───────────────────────────────────────────────

    async def _zerg_micro(self) -> None:
        await self._oracle_harassment()
        await self._storm_micro()
        await self._disruptor_nova()
        await self._archon_merge()

    async def _oracle_harassment(self) -> None:
        for oracle in self.units(UnitTypeId.ORACLE).idle:
            enemy_workers = self.enemy_units.filter(lambda u: u.type_id in _WORKER_TYPES)
            if enemy_workers:
                oracle.attack(enemy_workers.closest_to(oracle))
            elif self.enemy_structures:
                oracle.attack(self.enemy_structures.closest_to(oracle))
            elif self.enemy_start_locations:
                oracle.move(self.enemy_start_locations[0])

    async def _storm_micro(self) -> None:
        if self.already_pending_upgrade(UpgradeId.PSISTORMTECH) < 1:
            return
        for ht in self.units(UnitTypeId.HIGHTEMPLAR):
            if ht.energy < 75:
                continue
            abilities = await self.get_available_abilities(ht)
            if AbilityId.PSISTORM_PSISTORM not in abilities:
                continue
            nearby_enemies = self.enemy_units.closer_than(9, ht)
            if nearby_enemies.amount >= 5:
                ht(AbilityId.PSISTORM_PSISTORM, nearby_enemies.center)

    async def _disruptor_nova(self) -> None:
        for disruptor in self.units(UnitTypeId.DISRUPTOR).idle:
            abilities = await self.get_available_abilities(disruptor)
            if AbilityId.EFFECT_PURIFICATIONNOVA not in abilities:
                continue
            nearby_enemies = self.enemy_units.closer_than(13, disruptor)
            if nearby_enemies.amount >= 3:
                disruptor(AbilityId.EFFECT_PURIFICATIONNOVA, nearby_enemies.center)

    async def _archon_merge(self) -> None:
        low_energy_hts = [ht for ht in self.units(UnitTypeId.HIGHTEMPLAR) if ht.energy < 50]
        while len(low_energy_hts) >= 2:
            ht1, ht2 = low_energy_hts.pop(0), low_energy_hts.pop(0)
            if ht1.distance_to(ht2) < 4:
                ht1(AbilityId.MORPH_ARCHON)
                ht2(AbilityId.MORPH_ARCHON)
            else:
                ht1.move(ht2.position)
                ht2.move(ht1.position)

    async def _anti_creep_overlord(self) -> None:
        overlords = self.enemy_units.filter(lambda u: u.type_id == UnitTypeId.OVERLORD)
        if overlords:
            for stalker in self.units(UnitTypeId.STALKER).idle[:3]:
                closest = overlords.closest_to(stalker)
                if stalker.distance_to(closest) < 20:
                    stalker.attack(closest)

    async def on_end(self, game_result: Result) -> None:
        self._logger.log(
            "game_end",
            game_time=self.time,
            result=game_result.name,
            final_workers=self.workers.amount,
            final_bases=self.townhalls.amount,
            final_supply=self.supply_used,
            strategy=self._cheese_type or "standard_macro",
            opponent_race=self.enemy_race.name,
        )
        print(f"Game ended: {game_result}")
