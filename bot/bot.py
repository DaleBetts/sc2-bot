from __future__ import annotations

from sc2.bot_ai import BotAI
from sc2.data import Race, Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2


class CompetitiveBot(BotAI):
    NAME: str = "GrubbyBot"
    RACE: Race = Race.Protoss

    async def on_start(self) -> None:
        self.client.game_step = 2

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

        # Gateway — delay until 14 supply so we don't cut probes too early
        if (
            not self.structures(UnitTypeId.GATEWAY)
            and not self.already_pending(UnitTypeId.GATEWAY)
            and self.supply_used >= 14
            and self.can_afford(UnitTypeId.GATEWAY)
        ):
            await self._place_near(UnitTypeId.GATEWAY, pylon.position)

        # Assimilators — two per base
        if self.structures(UnitTypeId.GATEWAY) or self.already_pending(UnitTypeId.GATEWAY):
            await self._build_assimilators()

        # Cybernetics Core
        if (
            self.structures(UnitTypeId.GATEWAY).ready
            and not self.structures(UnitTypeId.CYBERNETICSCORE)
            and not self.already_pending(UnitTypeId.CYBERNETICSCORE)
            and self.can_afford(UnitTypeId.CYBERNETICSCORE)
        ):
            await self._place_near(UnitTypeId.CYBERNETICSCORE, pylon.position)

        if not self.structures(UnitTypeId.CYBERNETICSCORE).ready:
            return

        # Scale gateways with base count (cap 8)
        gw_total = (
            self.structures(UnitTypeId.GATEWAY).amount
            + self.structures(UnitTypeId.WARPGATE).amount
            + self.already_pending(UnitTypeId.GATEWAY)
        )
        target_gw = min(8, 2 + self.townhalls.amount)
        if gw_total < target_gw and self.can_afford(UnitTypeId.GATEWAY):
            await self._place_near(UnitTypeId.GATEWAY, pylon.position)

        # Robotics Facility — for Immortals and Colossus
        if (
            not self.structures(UnitTypeId.ROBOTICSFACILITY)
            and not self.already_pending(UnitTypeId.ROBOTICSFACILITY)
            and self.can_afford(UnitTypeId.ROBOTICSFACILITY)
        ):
            await self._place_near(UnitTypeId.ROBOTICSFACILITY, pylon.position)

        # Robotics Bay — for Colossus (Grubby deathball)
        if (
            self.structures(UnitTypeId.ROBOTICSFACILITY).ready
            and not self.structures(UnitTypeId.ROBOTICSBAY)
            and not self.already_pending(UnitTypeId.ROBOTICSBAY)
            and self.can_afford(UnitTypeId.ROBOTICSBAY)
        ):
            await self._place_near(UnitTypeId.ROBOTICSBAY, pylon.position)

        # Twilight Council — Blink then Charge, both Grubby essentials
        if (
            self.townhalls.amount >= 2
            and not self.structures(UnitTypeId.TWILIGHTCOUNCIL)
            and not self.already_pending(UnitTypeId.TWILIGHTCOUNCIL)
            and self.can_afford(UnitTypeId.TWILIGHTCOUNCIL)
        ):
            await self._place_near(UnitTypeId.TWILIGHTCOUNCIL, pylon.position)

        # Forge — ground weapon upgrades
        if (
            self.townhalls.amount >= 2
            and not self.structures(UnitTypeId.FORGE)
            and not self.already_pending(UnitTypeId.FORGE)
            and self.can_afford(UnitTypeId.FORGE)
        ):
            await self._place_near(UnitTypeId.FORGE, pylon.position)

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

    async def _gateway_units(self) -> None:
        pylons = self.structures(UnitTypeId.PYLON).ready
        if not pylons:
            return
        spawn_near = pylons.closest_to(self.start_location).position.towards(self.start_location, 3)

        # Warp Gates — Stalkers first (Grubby's core unit), Zealots as filler
        for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
            if self.supply_left <= 0:
                break
            abilities = await self.get_available_abilities(warpgate)
            if AbilityId.WARPGATETRAIN_STALKER in abilities and self.can_afford(UnitTypeId.STALKER):
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, spawn_near, placement_step=2)
                if placement:
                    warpgate(AbilityId.WARPGATETRAIN_STALKER, placement)
            elif AbilityId.WARPGATETRAIN_ZEALOT in abilities and self.can_afford(UnitTypeId.ZEALOT):
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, spawn_near, placement_step=2)
                if placement:
                    warpgate(AbilityId.WARPGATETRAIN_ZEALOT, placement)

        # Regular Gateways before warp gate research completes
        for gw in self.structures(UnitTypeId.GATEWAY).ready.idle:
            if self.supply_left <= 0:
                break
            if self.can_afford(UnitTypeId.STALKER):
                gw.train(UnitTypeId.STALKER)
            elif self.can_afford(UnitTypeId.ZEALOT):
                gw.train(UnitTypeId.ZEALOT)

    async def _robo_units(self) -> None:
        for robo in self.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle:
            if self.supply_left <= 0:
                break
            colossus_count = (
                self.units(UnitTypeId.COLOSSUS).amount + self.already_pending(UnitTypeId.COLOSSUS)
            )
            # Cap at 4 Colossus — any more and they become a liability vs Vikings
            if (
                self.structures(UnitTypeId.ROBOTICSBAY).ready
                and colossus_count < 4
                and self.can_afford(UnitTypeId.COLOSSUS)
            ):
                robo.train(UnitTypeId.COLOSSUS)
            elif self.can_afford(UnitTypeId.IMMORTAL):
                robo.train(UnitTypeId.IMMORTAL)

    # ── Upgrades ─────────────────────────────────────────────────────────────

    async def _research_upgrades(self) -> None:
        # Warp Gate — always first
        if (
            self.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0
            and self.can_afford(UpgradeId.WARPGATERESEARCH)
        ):
            self.structures(UnitTypeId.CYBERNETICSCORE).first.research(UpgradeId.WARPGATERESEARCH)

        # Blink — Grubby's signature, makes Stalkers nearly immortal with good micro
        if (
            self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
            and self.already_pending_upgrade(UpgradeId.BLINKTECH) == 0
            and self.can_afford(UpgradeId.BLINKTECH)
        ):
            self.structures(UnitTypeId.TWILIGHTCOUNCIL).first.research(UpgradeId.BLINKTECH)

        # Charge — Zealots become unstoppable, research after Blink
        if (
            self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
            and self.already_pending_upgrade(UpgradeId.CHARGE) == 0
            and self.already_pending_upgrade(UpgradeId.BLINKTECH) == 1
            and self.can_afford(UpgradeId.CHARGE)
        ):
            self.structures(UnitTypeId.TWILIGHTCOUNCIL).first.research(UpgradeId.CHARGE)

        # Extended Thermal Lance — doubles Colossus effective range
        if (
            self.structures(UnitTypeId.ROBOTICSBAY).ready
            and self.already_pending_upgrade(UpgradeId.EXTENDEDTHERMALANCE) == 0
            and self.can_afford(UpgradeId.EXTENDEDTHERMALANCE)
        ):
            self.structures(UnitTypeId.ROBOTICSBAY).first.research(UpgradeId.EXTENDEDTHERMALANCE)

        # +1/+2 Ground Weapons
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
        army_types = {UnitTypeId.STALKER, UnitTypeId.ZEALOT, UnitTypeId.COLOSSUS, UnitTypeId.IMMORTAL}
        army = self.units.filter(lambda u: u.type_id in army_types)

        if not army:
            return

        # Defend base first
        near_base = self.enemy_units.closer_than(25, self.start_location)
        if near_base:
            for unit in army:
                unit.attack(near_base.closest_to(unit))
            return

        # Rally near home until we have enough to commit — Grubby style timing attack
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
        """
        Blink critically low-HP Stalkers back toward our army.
        With good blink timing a Stalker can survive 3× longer — pure Grubby.
        """
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

    async def on_end(self, game_result: Result) -> None:
        print(f"Game ended: {game_result}")
