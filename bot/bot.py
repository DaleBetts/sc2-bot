from __future__ import annotations

from sc2.bot_ai import BotAI
from sc2.data import Race, Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2

_ARMY_TYPES = {
    UnitTypeId.STALKER,
    UnitTypeId.ZEALOT,
    UnitTypeId.COLOSSUS,
    UnitTypeId.IMMORTAL,
    UnitTypeId.ARCHON,
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

    @property
    def _vs_zerg(self) -> bool:
        return self.enemy_race == Race.Zerg

    async def on_step(self, iteration: int) -> None:
        if iteration == 0:
            await self.chat_send("gl hf - En Taro Artanis!")
        await self.distribute_workers()
        await self._build_pylons()
        await self._train_probes()
        await self._build_structures()
        await self._morph_warpgates()
        await self._produce_army()
        await self._research_upgrades()
        await self._expand()
        await self._attack()
        await self._stalker_blink_micro()
        if self._vs_zerg:
            await self._zerg_micro()
            await self._anti_creep_overlord()

    # ── Supply ───────────────────────────────────────────────────────────────

    async def _build_pylons(self) -> None:
        if (
            self.supply_cap < 200
            and self.supply_left < 5
            and self.already_pending(UnitTypeId.PYLON) < 2
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
        worker_cap = min(60, self.townhalls.amount * 22)
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

        gw_total = (
            self.structures(UnitTypeId.GATEWAY).amount
            + self.structures(UnitTypeId.WARPGATE).amount
            + self.already_pending(UnitTypeId.GATEWAY)
        )
        target_gw = min(8, 2 + self.townhalls.amount)
        if gw_total < target_gw and self.can_afford(UnitTypeId.GATEWAY):
            await self._place_near(UnitTypeId.GATEWAY, pylon.position)

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

        if (
            self.townhalls.amount >= 2
            and not self.structures(UnitTypeId.TWILIGHTCOUNCIL)
            and not self.already_pending(UnitTypeId.TWILIGHTCOUNCIL)
            and self.can_afford(UnitTypeId.TWILIGHTCOUNCIL)
        ):
            await self._place_near(UnitTypeId.TWILIGHTCOUNCIL, pylon.position)

        # Forge — earlier vs Zerg for faster weapon upgrades
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
        # Stargate — Oracle Drone harassment then Void Rays vs Corruptors
        if (
            not self.structures(UnitTypeId.STARGATE)
            and not self.already_pending(UnitTypeId.STARGATE)
            and self.can_afford(UnitTypeId.STARGATE)
        ):
            await self._place_near(UnitTypeId.STARGATE, pylon_pos)

        # Shield Batteries at natural — essential vs early Roach/Baneling pressure
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

        # Templar Archives — High Templar + Psionic Storm vs massed Ling/Hydra
        if (
            self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
            and not self.structures(UnitTypeId.TEMPLARARCHIVE)
            and not self.already_pending(UnitTypeId.TEMPLARARCHIVE)
            and self.can_afford(UnitTypeId.TEMPLARARCHIVE)
        ):
            await self._place_near(UnitTypeId.TEMPLARARCHIVE, pylon_pos)

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
        await self._robo_units()
        if self._vs_zerg and self.structures(UnitTypeId.STARGATE).ready:
            await self._stargate_units()

    async def _gateway_units(self) -> None:
        pylons = self.structures(UnitTypeId.PYLON).ready
        if not pylons:
            return
        spawn_near = pylons.closest_to(self.start_location).position.towards(self.start_location, 3)

        sentry_count = self.units(UnitTypeId.SENTRY).amount + self.already_pending(UnitTypeId.SENTRY)
        ht_count = self.units(UnitTypeId.HIGHTEMPLAR).amount + self.already_pending(UnitTypeId.HIGHTEMPLAR)
        archives_ready = bool(self.structures(UnitTypeId.TEMPLARARCHIVE).ready)

        for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
            if self.supply_left <= 0:
                break
            abilities = await self.get_available_abilities(warpgate)

            if (
                self._vs_zerg
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
                self._vs_zerg
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
            if self._vs_zerg and archives_ready and ht_count < 4 and self.can_afford(UnitTypeId.HIGHTEMPLAR):
                gw.train(UnitTypeId.HIGHTEMPLAR)
                ht_count += 1
            elif self.can_afford(UnitTypeId.STALKER):
                gw.train(UnitTypeId.STALKER)
            elif self._vs_zerg and sentry_count < 3 and self.can_afford(UnitTypeId.SENTRY):
                gw.train(UnitTypeId.SENTRY)
                sentry_count += 1
            elif self.can_afford(UnitTypeId.ZEALOT):
                gw.train(UnitTypeId.ZEALOT)

    async def _robo_units(self) -> None:
        # Zerg has no Vikings — cap Colossus higher; add Disruptors for Lurker/Hydra
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
            # First 2 Oracles harass Drones and force Spore Crawlers, delaying Zerg economy
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

        # Psionic Storm — essential for dealing with massed Hydra/Ling swarms
        if (
            self._vs_zerg
            and self.structures(UnitTypeId.TEMPLARARCHIVE).ready
            and self.already_pending_upgrade(UpgradeId.PSISTORMTECH) == 0
            and self.can_afford(UpgradeId.PSISTORMTECH)
        ):
            self.structures(UnitTypeId.TEMPLARARCHIVE).first.research(UpgradeId.PSISTORMTECH)

    # ── Expansion ─────────────────────────────────────────────────────────────

    async def _expand(self) -> None:
        target = 1 + (self.workers.amount // 22)
        if (
            self.townhalls.amount < target
            and not self.already_pending(UnitTypeId.NEXUS)
            and self.can_afford(UnitTypeId.NEXUS)
        ):
            await self.expand_now()

    # ── Attack ───────────────────────────────────────────────────────────────

    async def _attack(self) -> None:
        army_types = _ZERG_ARMY_TYPES if self._vs_zerg else _ARMY_TYPES
        army = self.units.filter(lambda u: u.type_id in army_types)

        if not army:
            return

        near_base = self.enemy_units.closer_than(25, self.start_location)
        if near_base:
            for unit in army:
                unit.attack(near_base.closest_to(unit))
            return

        rally = self.townhalls.random.position.towards(self.game_info.map_center, 15)
        if army.amount < 15:
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

    # ── Zerg-specific behaviors ───────────────────────────────────────────────

    async def _zerg_micro(self) -> None:
        await self._oracle_harassment()
        await self._storm_micro()
        await self._disruptor_nova()
        await self._archon_merge()

    async def _oracle_harassment(self) -> None:
        for oracle in self.units(UnitTypeId.ORACLE).idle:
            enemy_workers = self.enemy_units.filter(lambda u: u.is_worker)
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
            if AbilityId.EFFECT_PSISTORM not in abilities:
                continue
            nearby_enemies = self.enemy_units.closer_than(9, ht)
            if nearby_enemies.amount >= 5:
                ht(AbilityId.EFFECT_PSISTORM, nearby_enemies.center)

    async def _disruptor_nova(self) -> None:
        for disruptor in self.units(UnitTypeId.DISRUPTOR).idle:
            abilities = await self.get_available_abilities(disruptor)
            if AbilityId.EFFECT_PURIFICATIONNOVA not in abilities:
                continue
            nearby_enemies = self.enemy_units.closer_than(13, disruptor)
            if nearby_enemies.amount >= 3:
                disruptor(AbilityId.EFFECT_PURIFICATIONNOVA, nearby_enemies.center)

    async def _archon_merge(self) -> None:
        # Merge depleted High Templars into Archons — Archons are excellent vs Zerg
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
        # Deny vision and slow creep spread by targeting nearby Overlords with idle Stalkers
        overlords = self.enemy_units.filter(lambda u: u.type_id == UnitTypeId.OVERLORD)
        if overlords:
            for stalker in self.units(UnitTypeId.STALKER).idle[:3]:
                closest = overlords.closest_to(stalker)
                if stalker.distance_to(closest) < 20:
                    stalker.attack(closest)

    async def on_end(self, game_result: Result) -> None:
        print(f"Game ended: {game_result}")
