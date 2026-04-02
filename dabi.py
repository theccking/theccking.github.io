"""
THE CCDABI GAME
Copyright (c) M.Yan 2026
Licensed under the CC-BY-NC-SA 4.0 International license.
"""

import contextlib
import enum
import dataclasses as dc
import hashlib
import inspect
import ipaddress
import itertools
import json
import msvcrt
from os import system
import socket
from typing import Callable, Optional


class SkillCategory(enum.Enum):
    BASE = "基础游戏"
    REJECTS = "原版禁用内容"
    CCDC = "CDC 特殊内容"
    XIHAI = "西海模组"
    CCMOD = "CC国模组"
    JIAYA = "假牙模组"


class SkillType(enum.Enum):
    YIELDS = 1
    SHIELD = 2
    ATTACK = 3
    MISCEL = 4
    NOP = -1


CSI = "\033["
VERSION = "CCDabi v1.6.1"
UPDATE_NOTES = """\
THE CCDABI GAME
COPYRIGHT (C) M.YAN 2026, ALL RIGHTS RESERVED.

=== v1.6.1 ===
[CONTENT] 添加了『方辅刀』和『圆辅刀』。
[CONTENT] 完善了『方盾』和『圆盾』的防御机制。
[BUGFIX]  修复了被控时不能查看对方出招的问题。
[TECH]    重做了技能禁用系统。
<PAUSE>\
=== v1.5.3 ===
[BUGFIX]  缓解了网络连接导致的游戏崩溃问题。
[BUGFIX]  修复了“CDC 特殊内容”中盾牌的机制错误。

=== v1.5.1 ===
[FEATURE] 允许在一局游戏结束后继续游戏。
[FEATURE] 允许在回合结算界面查看全部技能的信息。
[FEATURE] 提供了『方盾』和『圆盾』的 1 点闪避数值。
[CONTENT] 更改了“自由搏击”系列技能的数值。
[BUGFIX]  缓解了网络连接导致的游戏开始时间不同步问题。
[BUGFIX]  修复了资源显示界面字符显示错误的问题。\
<PAUSE>\
=== v1.4.2 ===
[CONTENT] 现在『超闪』或『控』后不能打出『超神之力』。
[CONTENT] 添加了“CDC 特殊内容”分类。新增『棱盾』系列技能。
[CONTENT] “假牙”模组现已开放。
[CONTENT] 现在『单打独斗』可以使用任意元素打出。
[BUGFIX]  修复了资源信息显示中模组资源不显示和『攒』显示错误的问题。
[TECH]    添加了钩子 BEFOREROUND() AFTERROUND() BEFORESETTLE() 便于效果处理。\
<PAUSE>\
=== v1.3.1 ===
[FEATURE] 允许在回合结算界面查看双方资源信息。
[CONTENT] 添加了“原版禁用内容”分类。
[UI]      优化了房间创建和操作选择界面界面。
[TECH]    PREDICATOR() 现在可以操作敌方玩家数据。\
<PAUSE>\
=== v1.2.2 ===
[FEATURE] 增加了“无限”量值。
[FEATURE] 增加了部分技能的说明信息。
[UI]      优化了回合结算界面。
[BUGFIX]  盾牌控制回合计算错误已修复。\
<PAUSE>\
=== v1.1.3 ===
[FEATURE] 增加了模组支持。房间使用的模组将由房主在创建房间时确认。
[FEATURE] 增加了局域网内搜索房间功能。可以在菜单的“寻找游戏”中找到。
[UI]      优化了菜单和操作选择界面。
[BUGFIX]  闪避技能伤害计算错误已修复。
[BUGFIX]  盾牌控制回合无效果已修复。\
<PAUSE>\
=== v1.0.0 ===
[CONTENT] 实现了基础游戏内容。\
"""

_counter = 0


def iota():
    global _counter
    _counter += 1
    return _counter - 1


class Infinity:
    def __new__(cls, factor: "float | Infinity" = 1):
        if factor == 0:
            return 0
        else:
            return super().__new__(cls)

    def __init__(self, factor: "float | Infinity" = 1):
        self.factor: "float | Infinity" = factor

    def __mul__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return Infinity(self.factor * other)
        elif isinstance(other, Infinity):
            return Infinity(other * self.factor)
        else:
            return NotImplemented
    
    def __rmul__(self, other: "int | float | Infinity"):
        return self * other

    def __add__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return self
        elif isinstance(other, Infinity):
            return Infinity(self.factor + other.factor)
        else:
            return NotImplemented

    def __radd__(self, other: "int | float | Infinity"):
        return self + other

    def __sub__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return self
        elif isinstance(other, Infinity):
            return Infinity(self.factor - other.factor)
        else:
            return NotImplemented

    def __rsub__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return Infinity(-self.factor)
        elif isinstance(other, Infinity):
            return Infinity(other.factor - self.factor)
        else:
            return NotImplemented

    def __truediv__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return Infinity(self.factor / other)
        elif isinstance(other, Infinity):
            return Infinity(self.factor / other.factor)
        else:
            return NotImplemented

    def __rtruediv__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return Infinity(other / self.factor)
        elif isinstance(other, Infinity):
            return Infinity(other.factor / self.factor)
        else:
            return NotImplemented

    def __floordiv__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return Infinity(self.factor // other)
        elif isinstance(other, Infinity):
            return Infinity(self.factor // other.factor)
        else:
            return NotImplemented

    def __rfloordiv__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return Infinity(other // self.factor)
        elif isinstance(other, Infinity):
            return Infinity(other.factor // self.factor)
        else:
            return NotImplemented

    def __abs__(self):
        return Infinity(abs(self.factor))

    def __neg__(self):
        return Infinity(-self.factor)

    def __pos__(self):
        return Infinity(+self.factor)

    def __gt__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return self.factor > 0
        elif isinstance(other, Infinity):
            return self.factor > other.factor
        else:
            return NotImplemented

    def __ge__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return self.factor > 0
        elif isinstance(other, Infinity):
            return self.factor >= other.factor
        else:
            return NotImplemented

    def __lt__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return self.factor < 0
        elif isinstance(other, Infinity):
            return self.factor < other.factor
        else:
            return NotImplemented

    def __le__(self, other: "int | float | Infinity"):
        if isinstance(other, (int, float)):
            return self.factor < 0
        elif isinstance(other, Infinity):
            return self.factor <= other.factor
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, (int, float)):
            return False
        elif isinstance(other, Infinity):
            return self.factor == other.factor
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, (int, float)):
            return True
        elif isinstance(other, Infinity):
            return self.factor != other.factor
        else:
            return True

    def __repr__(self):
        return f"{self.factor} 倍率无限"


inf: Infinity = Infinity()  # type: ignore


@dc.dataclass(repr=False)
class Skill:
    name: str
    type: SkillType
    category: SkillCategory
    requirement: "Requirement"
    damage: float | Infinity = 0
    defense: float | Infinity = 0
    poisonRound: int = 0
    controlRound: int = 0
    disableSelf: bool = False
    desc: Optional[str] = None
    predicator: "Callable[[Player, Player], None]" = dc.field(
        default_factory=lambda: (lambda x, y: None)
    )
    on_break: "Callable[[Player, Player], None]" = dc.field(
        default_factory=lambda: (lambda x, y: None)
    )
    extra_check: "Callable[[Player], bool]" = dc.field(
        default_factory=lambda: (lambda x: True)
    )
    id: int = dc.field(default_factory=iota)

    def __mul__(self, n: int):
        return (self.id, n)

    def __repr__(self):
        return f"Skill<{self.type.name} {self.name} from {self.category.name}>"


class Requirement:
    def __init__(self):
        self.costs: list[tuple[int, int]] = []

    def includes(self, skill: int):
        return any(cost[0] == skill for cost in self.costs)

    def require(self, *cost: tuple[int, int]):
        self.costs.extend(cost)
        return self

    def __repr__(self):
        string = ""
        i = 0
        if len(self.costs) == 0:
            return "无"
        for cost in self.costs:
            if i > 0:
                string += "、"
            string += f"{cost[1]}个{game.skills[cost[0]].name}"
            i += 1
        return string


def require(*cost: tuple[int, int]) -> Requirement:
    return Requirement().require(*cost)


class RoundEffect:
    def __init__(self):
        self.clear()

    def clear(self):
        self.damageTaken: float | Infinity = 0
        self.endured: bool = False

    def endure(self):
        self.endured = True

    def offset(self, other: "RoundEffect"):
        self.damageTaken = max(self.damageTaken, 0)
        other.damageTaken = max(other.damageTaken, 0)
        tmp = self.damageTaken
        self.damageTaken = max(0, self.damageTaken - other.damageTaken)
        other.damageTaken = max(0, other.damageTaken - tmp)

    def reduce(self, amount: float):
        self.damageTaken -= amount

    def register(self, opponentSkill: Skill):
        self.damageTaken += opponentSkill.damage


@dc.dataclass
class Player:
    name: str
    hp: float | Infinity = 1.0
    roundsControlled: int = 0
    poisonRemaining: int = 0
    disableDistance: dict[int, int] = dc.field(default_factory=dict)
    disabled: list[int] = dc.field(default_factory=list)
    resources: dict[int, int] = dc.field(default_factory=dict)
    duplicatedResources: dict[int, int] = dc.field(default_factory=dict)
    roundEffect: RoundEffect = dc.field(init=False, default_factory=RoundEffect)
    skillPlayed: Skill | None = None
    defer: "list[Callable[[Player, Player], None]]" = dc.field(
        init=False, default_factory=list
    )
    beforeRound: "list[Callable[[Player, Player], None]]" = dc.field(
        init=False, default_factory=list
    )
    afterRound: "list[Callable[[Player, Player], None]]" = dc.field(
        init=False, default_factory=list
    )
    beforeSettle: "list[Callable[[Player, Player], None]]" = dc.field(
        init=False, default_factory=list
    )

    def getPossibleResource(self, skill: Skill | int | str):
        id: int
        if isinstance(skill, int):
            id = skill
        elif isinstance(skill, str):
            id = game.dict_skills[skill].id
        else:
            id = skill.id

        if id not in self.resources:
            return 0
        return self.resources[id]

    def _increaseDisableDistance(self, skill: int) -> int:
        self.disableDistance.setdefault(skill, 0)
        self.disableDistance[skill] += 1
        return self.disableDistance[skill]

    def _disableSingle(self, skill: Skill | int, waitUntil=1):
        if isinstance(skill, Skill):
            skill = skill.id

        if self._increaseDisableDistance(skill) == waitUntil:
            waitUntil = 0
            self.disabled.append(skill)

    def disable(self, *skills: Skill, waitUntil=1):
        for skill in skills:
            self._disableSingle(skill, waitUntil)

    def isValidPlay(self, skill: Skill):
        for cost in skill.requirement.costs:
            if self.getPossibleResource(game.skills[cost[0]]) < cost[1]:
                return False
        return skill.id not in self.disabled

    def consumeResource(self, requirement: Requirement):
        for cost in requirement.costs:
            self.resources[cost[0]] -= cost[1]
            if cost[0] in self.duplicatedResources:
                self.duplicatedResources[cost[0]] = max(
                    self.duplicatedResources[cost[0]] - cost[1], 0
                )

    def applyPoison(self):
        if self.poisonRemaining > 0:
            print(f"{CSI}32m剧毒 {CSI}0m{self.name} 受到 {CSI}31m1{CSI}0m 点剧毒伤害！")
            self.roundEffect.damageTaken += 1
            self.poisonRemaining -= 1

    def takeDamage(self, opponent: "Player") -> int:
        controlled_rounds = 0
        shields = self.shields

        if self.roundEffect.damageTaken == 0:
            return controlled_rounds

        pop_count = 0

        while self.roundEffect.damageTaken > 0 and len(shields) != 0:
            shield = shields.pop()
            shield.on_break(self, opponent)
            pop_count += 1
            self.resources[shield.id] -= 1
            print(f"{CSI}36m护盾 {CSI}0m{self.name} 的{shield.name}已经破碎！")

            self.roundEffect.damageTaken = max(
                0, self.roundEffect.damageTaken - shield.defense
            )
            print(
                f"{CSI}36m护盾 {CSI}0m{shield.name}为 {self.name} 抵挡了 {CSI}33m{shield.defense}{CSI}0m 点伤害，剩余伤害 {CSI}31m{self.roundEffect.damageTaken}{CSI}0m"
            )
            controlled_rounds += shield.controlRound
            if shield.controlRound > 0:
                print(
                    f"{CSI}33m控制 {CSI}0m{opponent.name} 被控制 {CSI}33m{shield.controlRound}{CSI}0m 回合！"
                )

        if isinstance(self.roundEffect.damageTaken, float):
            self.roundEffect.damageTaken = round(self.roundEffect.damageTaken, 2)

        print(
            f"{CSI}31m伤害 {CSI}0m{self.name} (HP: {CSI}33m{self.hp}{CSI}0m) 将承受{'剩余的' if pop_count > 0 else ''} {CSI}31m{self.roundEffect.damageTaken}{CSI}0m 点伤害"
        )

        if self.roundEffect.endured:
            print(
                f"{CSI}31m伤害 {CSI}0m{self.name} 回合内无敌！"
            )
        else:
            self.hp -= self.roundEffect.damageTaken

        return controlled_rounds

    @property
    def shields(self):
        shields: list[Skill] = []
        for resource, count in self.resources.items():
            if (skill := game.skills[resource]).type == SkillType.SHIELD:
                shields.extend([skill] * count)
        return shields


@dc.dataclass
class RoundAction:
    actionType: SkillType
    skillId: int

    def pack(self) -> bytes:
        return f"{self.actionType.value}|{self.skillId}".encode()

    @staticmethod
    def unpack(data: bytes):
        actionType, skillId = map(int, data.decode().split("|"))
        return RoundAction(SkillType(actionType), skillId)


class UserInterface:
    def chooseHostGuest(
        self, roomsInvoker: Callable[[], list[tuple[str, dict]]]
    ) -> tuple[int, str, str]:
        chosen = 0
        system("cls")
        print("=" * 10, VERSION, "=" * 10)
        print("你可以按 [v] 键查看版本更新信息。强烈推荐您在版本更新后查看该信息。")
        print("你可以按 [q] 键完全退出游戏。")
        print("\n\n")
        while True:
            print(f"{CSI}3A{CSI}J", end="")
            if chosen == 0:
                print("> " + CSI + "47;30m创建房间（作为房主）" + CSI + "0m")
                print("  寻找游戏（作为访客）")
                print("  加入房间（作为访客）")
            elif chosen == 1:
                print("  创建房间（作为房主）")
                print("> " + CSI + "47;30m寻找游戏（作为访客）" + CSI + "0m")
                print("  加入房间（作为访客）")
            else:
                print("  创建房间（作为房主）")
                print("  寻找游戏（作为访客）")
                print("> " + CSI + "47;30m加入房间（作为访客）" + CSI + "0m")

            lagDfd = 1
            while lagDfd:
                lagDfd = 0
                ch = msvcrt.getch()
                if ch == b"\xe0":
                    arrow = msvcrt.getch()
                    if arrow == b"H":
                        chosen = (chosen - 1) % 3
                    elif arrow == b"P":
                        chosen = (chosen + 1) % 3
                elif ch == b"w":
                    chosen = (chosen - 1) % 3
                elif ch == b"b":
                    chosen = (chosen + 1) % 3
                elif ch == b" " or ch == b"\r":
                    username = input("输入你的用户名：")
                    if chosen == 0:
                        return 0, username, "0.0.0.0"
                    elif chosen == 1:
                        return 1, username, self.selectRoom(roomsInvoker())
                    else:
                        return 1, username, input("输入房间IP：")
                elif ch == b"v":
                    self.updateNotes()
                    system("cls")
                    print("=" * 10, VERSION, "=" * 10)
                    print("你可以按 [v] 键查看版本更新信息。")
                    print("你可以按 [q] 键完全退出游戏。")
                    print("\n\n")
                elif ch == b"q":
                    raise SystemExit(0)
                else:
                    lagDfd = 1

    def updateNotes(self):
        system("cls")
        print("=" * 10, VERSION, "=" * 10)
        print()
        notes = UPDATE_NOTES.strip().split("<PAUSE>")
        for i, note in enumerate(notes):
            print(note.strip())
            if i < len(notes) - 1:
                print("=" * 5, "按任意键继续或 [q] 退出。", "=" * 5)
                ch = msvcrt.getch()
                print("\033[F\033[K")
                if ch == b"q":
                    return
        print()
        print("=" * 5, "显示完毕，按任意键退出。", "=" * 5)
        msvcrt.getch()

    def selectSuits(self) -> set[SkillCategory]:
        system("cls")

        disabled = ()
        required = (SkillCategory.BASE,)
        selected: set[SkillCategory] = set(required)
        hovering = 0

        categories = [c for c in SkillCategory]

        print("=" * 10, VERSION, "- 选择游戏套装", "=" * 10)
        print("\n" * (len(categories)), end="")
        while True:
            print(f"{CSI}{len(categories)}A{CSI}J", end="")
            for i, category in enumerate(SkillCategory):
                output = ""
                if category in disabled:
                    output += f"{CSI}90m[-] "
                elif category in required:
                    output += f"{CSI}90m[+] "
                else:
                    output += f"[{CSI}32m+{CSI}0m] " if category in selected else "[ ] "
                if i == hovering:
                    output += f"{CSI}47;30m"
                output += f"{category.value}{CSI}0m"
                print(output)

            lagDfd = 1
            while lagDfd:
                lagDfd = 0
                ch = msvcrt.getch()
                if ch == b"\xe0":
                    arrow = msvcrt.getch()
                    if arrow == b"H":
                        hovering = (hovering - 1) % len(SkillCategory)
                    elif arrow == b"P":
                        hovering = (hovering + 1) % len(SkillCategory)
                elif ch == b"w":
                    hovering = (hovering - 1) % len(SkillCategory)
                elif ch == b"b":
                    hovering = (hovering + 1) % len(SkillCategory)
                elif ch == b" ":
                    if (
                        categories[hovering] not in disabled
                        and categories[hovering] not in required
                    ):
                        if categories[hovering] in selected:
                            selected.remove(categories[hovering])
                        else:
                            selected.add(categories[hovering])
                elif ch == b"\r":
                    return selected
                else:
                    lagDfd = 1

    def selectRoom(self, rooms: list[tuple[str, dict]]) -> str:
        chosen = 0
        if len(rooms) == 0:
            system("cls")
            print("=" * 10, VERSION, "- 寻找游戏", "=" * 10)
            print("未找到可用的房间！")
            return input("请手动输入房间IP：")
        while True:
            system("cls")
            print("=" * 10, VERSION, "- 寻找游戏", "=" * 10)
            for i, room in enumerate(rooms):
                print(
                    f"{'> ' + CSI + '47;30m' if i == chosen else '  '}{room[1]['host']} 的房间"
                    + CSI
                    + "0m"
                )
                suits = set(SkillCategory[c] for c in room[1]["suits"])
                if i == chosen:
                    print(f"    {CSI}90m房间 IP：{CSI}0m{room[0]}")
                    print(
                        f"    {CSI}90m模组套装：{CSI}0m{'、'.join(map(lambda x: x.value, suits))}"
                    )

            lagDfd = 1
            while lagDfd:
                lagDfd = 0
                ch = msvcrt.getch()
                if ch == b"\xe0":
                    arrow = msvcrt.getch()
                    if arrow == b"H":
                        chosen = max(0, chosen - 1)
                    elif arrow == b"P":
                        chosen = min(len(rooms) - 1, chosen + 1)
                elif ch == b"w":
                    chosen = max(0, chosen - 1)
                elif ch == b"b":
                    chosen = min(len(rooms) - 1, chosen + 1)
                elif ch == b" " or ch == b"\r":
                    return rooms[chosen][0]
                else:
                    lagDfd = 1

    def chooseAction(self, n: int, skills: list[Skill]):
        yields: list[Skill] = []
        attack: list[Skill] = []
        shield: list[Skill] = []
        miscel: list[Skill] = []
        mapping: dict[tuple[int, int], int] = {}

        for skill in skills:
            if skill.type == SkillType.YIELDS:
                mapping[(1, len(yields))] = skill.id
                yields.append(skill)

            elif skill.type == SkillType.SHIELD:
                mapping[(2, len(shield))] = skill.id
                shield.append(skill)

            elif skill.type == SkillType.ATTACK:
                mapping[(3, len(attack))] = skill.id
                attack.append(skill)

            elif skill.type == SkillType.MISCEL:
                mapping[(4, len(miscel))] = skill.id
                miscel.append(skill)

        lengths = [0, len(yields), len(shield), len(attack), len(miscel)]

        selected_type = 1
        selected_skill = -1

        while True:
            system("cls")
            print("=" * 10, f"第 {n} 回合 选择", "=" * 10)
            print(
                f"{'v ' + CSI + '47;30m' if selected_type == 1 else '> '}积攒资源"
                + CSI
                + "0m"
            )
            if selected_type == 1:
                for i, skill in enumerate(yields):
                    print(
                        f"  {'> ' + CSI + '42;30m' if i == selected_skill else '  '}{skill.name}"
                        + CSI
                        + "0m"
                    )
                    if i == selected_skill and skill.desc is not None:
                        print(f"    {CSI}90m{skill.desc}{CSI}0m")

            print(
                f"{'v ' + CSI + '47;30m' if selected_type == 2 else '> '}佩戴盾牌"
                + CSI
                + "0m"
            )
            if selected_type == 2:
                for i, skill in enumerate(shield):
                    print(
                        f"  {'> ' + CSI + '42;30m' if i == selected_skill else '  '}{skill.name}"
                        + CSI
                        + "0m"
                    )
                    if i == selected_skill:
                        if skill.desc is not None:
                            print(f"    {CSI}90m{skill.desc}{CSI}0m")
                        print(f"    {CSI}90m消耗资源：{CSI}0m{skill.requirement}")
                        print(f"    {CSI}90m防御力：{CSI}0m{skill.defense}")
                        print(f"    {CSI}90m控制回合数：{CSI}0m{skill.controlRound}")

            print(
                f"{'v ' + CSI + '47;30m' if selected_type == 3 else '> '}进攻对手"
                + CSI
                + "0m"
            )
            if selected_type == 3:
                for i, skill in enumerate(attack):
                    print(
                        f"  {'> ' + CSI + '42;30m' if i == selected_skill else '  '}{skill.name}"
                        + CSI
                        + "0m"
                    )
                    if i == selected_skill:
                        if skill.desc is not None:
                            print(f"    {CSI}90m{skill.desc}{CSI}0m")
                        print(f"    {CSI}90m消耗资源：{CSI}0m{skill.requirement}")
                        print(f"    {CSI}90m造成伤害：{CSI}0m{skill.damage}")
                        print(f"    {CSI}90m剧毒持续：{CSI}0m{skill.poisonRound}")

            print(
                f"{'v ' + CSI + '47;30m' if selected_type == 4 else '> '}特殊操作"
                + CSI
                + "0m"
            )
            if selected_type == 4:
                for i, skill in enumerate(miscel):
                    print(
                        f"  {'> ' + CSI + '42;30m' if i == selected_skill else '  '}{skill.name}"
                        + CSI
                        + "0m"
                    )
                    if i == selected_skill:
                        if skill.desc is not None:
                            print(f"    {CSI}90m{skill.desc}{CSI}0m")
                        print(f"    {CSI}90m消耗资源：{CSI}0m{skill.requirement}")

            lagDfd = 1
            while lagDfd:
                lagDfd = 0
                ch = msvcrt.getch()
                # 上下左右箭头控制
                if ch == b"\r" and selected_skill != -1:
                    return mapping[(selected_type, selected_skill)]
                elif ch == b"\xe0":
                    arrow = msvcrt.getch()
                    if arrow == b"H":
                        if selected_skill == 0:
                            selected_skill = -1
                        elif selected_skill == -1:
                            selected_type = max(1, selected_type - 1)
                            selected_skill = -1
                        else:
                            selected_skill -= 1

                    elif arrow == b"P":
                        if selected_skill == lengths[selected_type] - 1:
                            selected_type = min(4, selected_type + 1)
                            selected_skill = -1
                        else:
                            selected_skill += 1

                elif ch == b"w":
                    selected_type = min(4, selected_type + 1)
                    selected_skill = -1

                elif ch == b"b":
                    selected_type = max(1, selected_type - 1)
                    selected_skill = -1

                else:
                    lagDfd = 1

    def viewActions(
        self, n: int, skills: list[Skill], isAvailable: Callable[[Skill], bool]
    ):
        yields: list[Skill] = []
        attack: list[Skill] = []
        shield: list[Skill] = []
        miscel: list[Skill] = []
        mapping: dict[tuple[int, int], int] = {}

        for skill in skills:
            if skill.type == SkillType.YIELDS:
                mapping[(1, len(yields))] = skill.id
                yields.append(skill)

            elif skill.type == SkillType.SHIELD:
                mapping[(2, len(shield))] = skill.id
                shield.append(skill)

            elif skill.type == SkillType.ATTACK:
                mapping[(3, len(attack))] = skill.id
                attack.append(skill)

            elif skill.type == SkillType.MISCEL:
                mapping[(4, len(miscel))] = skill.id
                miscel.append(skill)

        lengths = [0, len(yields), len(shield), len(attack), len(miscel)]

        selected_type = 1
        selected_skill = -1

        while True:
            system("cls")
            print("=" * 10, f"第 {n} 回合 选择", "=" * 10)
            print(
                f"{'v ' + CSI + '47;30m' if selected_type == 1 else '> '}积攒资源"
                + CSI
                + "0m"
            )
            if selected_type == 1:
                for i, skill in enumerate(yields):
                    print(
                        f"  {'> ' + CSI + ('42;30m' if isAvailable(skill) else '41;30m') if i == selected_skill else '  '}{skill.name} "
                        + CSI
                        + "0m"
                    )
                    if i == selected_skill and skill.desc is not None:
                        print(f"    {CSI}90m{skill.desc}{CSI}0m")

            print(
                f"{'v ' + CSI + '47;30m' if selected_type == 2 else '> '}佩戴盾牌"
                + CSI
                + "0m"
            )
            if selected_type == 2:
                for i, skill in enumerate(shield):
                    print(
                        f"  {'> ' + CSI + ('42;30m' if isAvailable(skill) else '41;30m') if i == selected_skill else '  '}{skill.name}"
                        + CSI
                        + "0m"
                    )
                    if i == selected_skill:
                        if skill.desc is not None:
                            print(f"    {CSI}90m{skill.desc}{CSI}0m")
                        print(f"    {CSI}90m需要资源：{CSI}0m{skill.requirement}")
                        print(f"    {CSI}90m防御力：{CSI}0m{skill.defense}")
                        print(f"    {CSI}90m控制回合数：{CSI}0m{skill.controlRound}")

            print(
                f"{'v ' + CSI + '47;30m' if selected_type == 3 else '> '}进攻对手"
                + CSI
                + "0m"
            )
            if selected_type == 3:
                for i, skill in enumerate(attack):
                    print(
                        f"  {'> ' + CSI + ('42;30m' if isAvailable(skill) else '41;30m') if i == selected_skill else '  '}{skill.name}"
                        + CSI
                        + "0m"
                    )
                    if i == selected_skill:
                        if skill.desc is not None:
                            print(f"    {CSI}90m{skill.desc}{CSI}0m")
                        print(f"    {CSI}90m需要资源：{CSI}0m{skill.requirement}")
                        print(f"    {CSI}90m造成伤害：{CSI}0m{skill.damage}")
                        print(f"    {CSI}90m剧毒持续：{CSI}0m{skill.poisonRound}")

            print(
                f"{'v ' + CSI + '47;30m' if selected_type == 4 else '> '}特殊操作"
                + CSI
                + "0m"
            )
            if selected_type == 4:
                for i, skill in enumerate(miscel):
                    print(
                        f"  {'> ' + CSI + ('42;30m' if isAvailable(skill) else '41;30m') if i == selected_skill else '  '}{skill.name}"
                        + CSI
                        + "0m"
                    )
                    if i == selected_skill:
                        if skill.desc is not None:
                            print(f"    {CSI}90m{skill.desc}{CSI}0m")
                        print(f"    {CSI}90m需要资源：{CSI}0m{skill.requirement}")

            lagDfd = 1
            while lagDfd:
                lagDfd = 0
                ch = msvcrt.getch()
                # 上下左右箭头控制
                if ch == b"\r" or ch == b"q":
                    return
                elif ch == b"\xe0":
                    arrow = msvcrt.getch()
                    if arrow == b"H":
                        if selected_skill == 0:
                            selected_skill = -1
                        elif selected_skill == -1:
                            selected_type = max(1, selected_type - 1)
                            selected_skill = -1
                        else:
                            selected_skill -= 1

                    elif arrow == b"P":
                        if selected_skill == lengths[selected_type] - 1:
                            selected_type = min(4, selected_type + 1)
                            selected_skill = -1
                        else:
                            selected_skill += 1

                elif ch == b"w":
                    selected_type = min(4, selected_type + 1)
                    selected_skill = -1

                elif ch == b"b":
                    selected_type = max(1, selected_type - 1)
                    selected_skill = -1

                else:
                    lagDfd = 1

    def tryShowMaterials(self, n: int, localPlayer: Player, remotePlayer: Player):
        print("==> [b]: 查看双方资源")
        print("==> [c]: 查看全部技能")
        print("==> 按任意键进行下一回合...")
        ch = msvcrt.getch()
        if ch == b"b":
            self.showMaterials(n, game)
            system("cls")
        elif ch == b"c":
            self.viewActions(
                n, game.skills, lambda x: game.isSkillAvailable(game.localPlayer, x)
            )
        else:
            return

    def showMaterials(self, n: int, game: "Game"):
        yields: list[Skill] = []
        for skill in game.skills:
            if skill.type == SkillType.YIELDS:
                yields.append(skill)

        system("cls")
        print("=" * 10, f"第 {n} 回合 - 资源信息", "=" * 10)
        print(f"=== {CSI}92m友方资源{CSI}0m ===")

        for i, skill in enumerate(yields):
            print(
                f"  {CSI}90m{skill.name}{CSI}33m{game.localPlayer.getPossibleResource(skill.id)}{CSI}0m"
            )

        print(f"=== {CSI}91m对手资源{CSI}0m ===")

        for i, skill in enumerate(yields):
            print(
                f"  {CSI}90m{skill.name}{CSI}33m{game.remotePlayer.getPossibleResource(skill.id)}{CSI}0m"
            )

        print("=== 按任意键继续 ===")
        msvcrt.getch()


PORT = 8878


class Game:
    localPlayer: Player
    remotePlayer: Player

    sock: socket.socket
    isHost: bool
    gameReady: bool
    skills: list[Skill]
    dict_skills: dict[str, Skill]
    suits: set[SkillCategory]

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gameReady = False
        self.skills = []
        self.dict_skills = {}
        self.suits = set()
        self.localPlayer = Player("Anonymous")
        self.remotePlayer = Player("Anonymous")
        self.ui = UserInterface()

    def asHost(self) -> bool:
        self.isHost = True
        self.suits = self.ui.selectSuits()

        self.sock.bind(("0.0.0.0", PORT))
        self.sock.listen(1)

        system("cls")
        print("=" * 10, VERSION, "- 创建房间", "=" * 10)
        print(f"{CSI}90m主机玩家：{CSI}0m{self.localPlayer.name}")
        print(
            f"{CSI}90m模组套装：{CSI}36m{'、'.join(c.value for c in self.suits)}{CSI}0m"
        )
        print("房间创建成功，等待对手连接...")

        self.gameReady = False
        client, _ = self.sock, ("0.0.0.0", PORT)

        while not self.gameReady:
            client, _ = self.sock.accept()
            try:
                handshake = client.recv(64)
                if handshake == b"CCDABI_GUEST_IS_READY":
                    self.gameReady = True
                    self.sock = client
                elif handshake == b"CCDABI_GUEST_REQUEST_INFO":
                    client.send(
                        json.dumps(
                            {
                                "host": self.localPlayer.name,
                                "suits": [c.name for c in self.suits],
                            }
                        ).encode()
                    )
                    client.close()
            except socket.error:
                if not client._closed:
                    client.close()
                continue

        # self.sock.close()
        self.sock = client
        self.sock.send(json.dumps([c.name for c in self.suits]).encode())

        print("对手已连接！")
        return True

    def asGuest(self, address: str) -> bool:
        self.isHost = False
        try:
            self.sock.connect((address, PORT))
            self.sock.sendall(b"CCDABI_GUEST_IS_READY")
            suits = json.loads(self.sock.recv(1024).decode())
            self.suits = set(SkillCategory[c] for c in suits)
            self.gameReady = True
        except Exception:
            print("连接失败！请检查地址是否正确")
            self.sock.close()
            return False
        print("连接成功！")
        return True

    def syncPlayerInfo(self) -> bool:
        if not self.guardian():
            return False
        try:
            self.sock.send(self.localPlayer.name.encode())
            remote_name = self.sock.recv(64)
        except Exception:
            print("同步用户信息失败！")
            return False

        self.remotePlayer.name = remote_name.decode()
        system("cls")
        print("=" * 10, VERSION, "- 对战信息", "=" * 10)
        print(f"{CSI}90m你：{CSI}0m{self.localPlayer.name}")
        print(f"{CSI}90m对手：{CSI}0m{self.remotePlayer.name}")
        print("游戏加载完成！按任意键准备游戏...")
        msvcrt.getch()
        self.sock.sendall(b"CCDABI_PLAYER_READY")
        print("等待对手准备游戏...")
        handshake = self.sock.recv(64)
        while handshake != b"CCDABI_PLAYER_READY":
            handshake = self.sock.recv(64)
        return True

    def initSkills(self, *categories: SkillCategory):
        self.skills.clear()
        self.dict_skills.clear()
        # === 货币 ===

        self.skills.append(
            fangdun := Skill(
                "方盾",
                SkillType.YIELDS,
                SkillCategory.BASE,
                require(),
                predicator=lambda x, y: self.execute_protect_from(x, y, fangdun, dabi, fang_fudao),
            )
        )

        self.skills.append(
            yuandun := Skill(
                "圆盾",
                SkillType.YIELDS,
                SkillCategory.BASE,
                require(),
                predicator=lambda x, y: self.execute_protect_from(x, y, yuandun, zan, yuan_fudao),
            )
        )

        self.skills.append(
            zan := Skill(
                "攒",
                SkillType.YIELDS,
                SkillCategory.BASE,
                require(),
            )
        )

        self.skills.append(
            dabi := Skill(
                "大臂",
                SkillType.YIELDS,
                SkillCategory.BASE,
                require(),
            )
        )

        self.skills.append(
            chaoshen := Skill(
                "超神之力",
                SkillType.YIELDS,
                SkillCategory.BASE,
                require(),
                disableSelf=True
            )
        )

        # === 盾牌 ===

        self.skills.append(
            shandiandun := Skill(
                "闪电盾",
                SkillType.SHIELD,
                SkillCategory.BASE,
                require(fangdun * 2, dabi * 1),
                defense=3.0,
                controlRound=2,
            )
        )

        self.skills.append(
            leidiandun := Skill(
                "雷电盾",
                SkillType.SHIELD,
                SkillCategory.BASE,
                require(yuandun * 2, zan * 1),
                defense=2.0,
                controlRound=3,
            )
        )

        self.skills.append(
            yuansudun := Skill(
                "元素盾",
                SkillType.SHIELD,
                SkillCategory.BASE,
                require(fangdun * 1, yuandun * 1, zan * 1, dabi * 1),
                defense=inf * 0.25,
                controlRound=2,
            )
        )

        self.skills.append(
            milkdun := Skill(
                "奶声奶气盾",
                SkillType.SHIELD,
                SkillCategory.BASE,
                require(fangdun * 1, yuandun * 1, zan * 1, dabi * 1),
                defense=1.0,
                controlRound=4,
            )
        )

        self.skills.append(
            milkdun := Skill(
                "四脚朝天盾",
                SkillType.SHIELD,
                SkillCategory.BASE,
                require(fangdun * 8, yuandun * 8),
                defense=inf * 10,
            )
        )

        # === 基础攻击 ===
        self.skills.append(
            fang_fudao := Skill(
                "方辅刀", 
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(),
                damage=0.05,
                disableSelf=True
            )
        )

        self.skills.append(
            yuan_fudao := Skill(
                "圆辅刀",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(),
                damage=0.1,
                predicator=self.execute_disable_attack
            )
        )

        # === 锤系 ===

        self.skills.append(
            chui := Skill(
                "锤",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 1, dabi * 1),
                damage=2.5,
            )
        )

        self.skills.append(
            chui3 := Skill(
                "锤 (x3)",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 3, dabi * 3),
                damage=7.5,
            )
        )

        self.skills.append(
            chui5 := Skill(
                "锤 (x5)",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 5, dabi * 5),
                damage=12.5,
            )
        )

        self.skills.append(
            chui7 := Skill(
                "锤 (x7)",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 7, dabi * 7),
                damage=17.5,
            )
        )

        self.skills.append(
            chui9 := Skill(
                "锤 (x9)",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 9, dabi * 9),
                damage=22.5,
            )
        )

        self.skills.append(
            chui11 := Skill(
                "锤 (x11)",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 11, dabi * 11),
                damage=inf,
            )
        )

        self.skills.append(
            chui21 := Skill(
                "锤 (x21)",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 21, dabi * 21),
                damage=inf * 2,
            )
        )

        # === 基础型 ===

        self.skills.append(
            punch := Skill(
                "拳",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(fangdun * 1),
                damage=0.8,
            )
        )

        self.skills.append(
            punch2 := Skill(
                "连拳",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(fangdun * 2),
                damage=1.6,
            )
        )

        self.skills.append(
            punch3 := Skill(
                "三连拳",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(fangdun * 3),
                damage=2.4,
            )
        )

        self.skills.append(
            punch4 := Skill(
                "重拳",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(fangdun * 4),
                damage=4.8,
            )
        )

        self.skills.append(
            kick := Skill(
                "脚",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(yuandun * 1),
                damage=0.6,
            )
        )

        self.skills.append(
            kick2 := Skill(
                "连脚",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(yuandun * 2),
                damage=1.2,
            )
        )

        self.skills.append(
            kick3 := Skill(
                "三连脚",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(yuandun * 3),
                damage=2.5,
            )
        )

        self.skills.append(
            kick4 := Skill(
                "重脚",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(yuandun * 4),
                damage=4.2,
            )
        )

        self.skills.append(
            chop := Skill(
                "刀",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(dabi * 1),
                damage=1.0,
            )
        )

        self.skills.append(
            chop2 := Skill(
                "连刀",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(dabi * 2),
                damage=2.0,
            )
        )

        self.skills.append(
            chop3 := Skill(
                "大砍刀",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(dabi * 3),
                damage=3.0,
            )
        )

        self.skills.append(
            chop4 := Skill(
                "青龙偃月刀",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(dabi * 4),
                damage=4.0,
            )
        )

        self.skills.append(
            ber := Skill(
                "BER",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 1),
                damage=1.0,
            )
        )

        self.skills.append(
            ber2 := Skill(
                "连 BER",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 2),
                damage=2.0,
            )
        )

        self.skills.append(
            ber3 := Skill(
                "海浪",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 3),
                damage=3.0,
            )
        )

        self.skills.append(
            ber4 := Skill(
                "惊涛骇浪",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 4),
                damage=4.0,
            )
        )

        # === 复合型 ===

        self.skills.append(
            beat := Skill(
                "拳打脚踢",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(fangdun * 1, yuandun * 1),
                damage=1.4,
            )
        )

        self.skills.append(
            beat4 := Skill(
                "重拳重脚",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(fangdun * 4, yuandun * 4),
                damage=11.0,
            )
        )

        self.skills.append(
            strike := Skill(
                "雷劈",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(yuandun * 3, zan * 1),
                damage=8.0,
            )
        )

        self.skills.append(
            strike2 := Skill(
                "大雷劈",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(yuandun * 9, zan * 3),
                damage=40.0,
            )
        )

        self.skills.append(
            nuclear := Skill(
                "核废水",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(fangdun * 3, dabi * 1),
                damage=5.0,
                poisonRound=3,
            )
        )

        self.skills.append(
            nausea := Skill(
                "水土不服",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(yuandun * 1, zan * 1),
                damage=2.2,
            )
        )

        self.skills.append(
            loser := Skill(
                "水瓶低",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(fangdun * 1, zan * 1),
                damage=2.2,
            )
        )

        self.skills.append(
            lightning := Skill(
                "球状闪电",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(shandiandun * 1, leidiandun * 1, yuansudun * 1),
                damage=114.514,
            )
        )

        self.skills.append(
            duel_f := Skill(
                "单打独斗【方盾】",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(fangdun * 15),
                damage=inf * 0.5,
            )
        )

        self.skills.append(
            duel_y := Skill(
                "单打独斗【圆盾】",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(yuandun * 15),
                damage=inf * 0.5,
            )
        )

        self.skills.append(
            duel_z := Skill(
                "单打独斗【攒】",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(zan * 15),
                damage=inf * 0.5,
            )
        )

        self.skills.append(
            duel_d := Skill(
                "单打独斗【大臂】",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(dabi * 15),
                damage=inf * 0.5,
            )
        )

        self.skills.append(
            bang := Skill(
                "宇宙大爆炸 - 回合内无敌",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(dabi * 30),
                predicator=lambda x, y: x.roundEffect.endure(),
            )
        )

        self.skills.append(
            massacre := Skill(
                "横 扫 千 军",
                SkillType.ATTACK,
                SkillCategory.BASE,
                require(bang * 1),
                damage=inf,
            )
        )

        # === 闪避型 ===

        self.skills.append(
            shan := Skill(
                "闪",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(),
                desc="提供 2 点伤害免疫。",
                predicator=lambda x, y: (x.disable(shan, waitUntil=2), x.roundEffect.reduce(2))[-1],
            )
        )

        self.skills.append(
            supershan := Skill(
                "超闪",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(),
                desc="提供 10 点伤害免疫。",
                disableSelf=True,
                predicator=lambda x, y: (x.disable(shan, kong), x.roundEffect.reduce(10))[-1],
            )
        )

        self.skills.append(
            kong := Skill(
                "控",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(chaoshen * 1),
                desc="提供 114514.19 点伤害免疫。",
                disableSelf=True,
                predicator=lambda x, y: (x.disable(supershan), x.roundEffect.reduce(114514.19))[-1],
            )
        )

        # === 机制类 ===

        self.skills.append(
            fangdun_producer := Skill(
                "方盾 的 小型生产器",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(fangdun * 2),
                predicator=lambda x, y: self.execute_duplicator(x, fangdun, 2, 2),
                extra_check=lambda x: self.check_duplicator(x, fangdun, 2),
            )
        )

        self.skills.append(
            fangdun_duplicator := Skill(
                "方盾 的 大型生产器",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(fangdun * 4),
                predicator=lambda x, y: self.execute_duplicator(x, fangdun, 4, 5),
                extra_check=lambda x: self.check_duplicator(x, fangdun, 4),
            )
        )

        self.skills.append(
            yuandun_producer := Skill(
                "圆盾 的 小型生产器",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(yuandun * 2),
                predicator=lambda x, y: self.execute_duplicator(x, yuandun, 2, 2),
                extra_check=lambda x: self.check_duplicator(x, yuandun, 2),
            )
        )

        self.skills.append(
            yuandun_duplicator := Skill(
                "圆盾 的 大型生产器",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(yuandun * 4),
                predicator=lambda x, y: self.execute_duplicator(x, yuandun, 4, 5),
                extra_check=lambda x: self.check_duplicator(x, yuandun, 4),
            )
        )

        self.skills.append(
            zan_producer := Skill(
                "攒 的 小型生产器",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(zan * 2),
                predicator=lambda x, y: self.execute_duplicator(x, zan, 2, 2),
                extra_check=lambda x: self.check_duplicator(x, zan, 2),
            )
        )

        self.skills.append(
            zan_duplicator := Skill(
                "攒 的 大型生产器",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(zan * 4),
                predicator=lambda x, y: self.execute_duplicator(x, zan, 4, 5),
                extra_check=lambda x: self.check_duplicator(x, zan, 4),
            )
        )

        self.skills.append(
            dabi_producer := Skill(
                "大臂 的 小型生产器",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(dabi * 2),
                predicator=lambda x, y: self.execute_duplicator(x, dabi, 2, 2),
                extra_check=lambda x: self.check_duplicator(x, dabi, 2),
            )
        )

        self.skills.append(
            dabi_duplicator := Skill(
                "大臂 的 大型生产器",
                SkillType.MISCEL,
                SkillCategory.BASE,
                require(dabi * 4),
                predicator=lambda x, y: self.execute_duplicator(x, dabi, 4, 5),
                extra_check=lambda x: self.check_duplicator(x, dabi, 4),
            )
        )

        # === MOD 内容 ===

        if SkillCategory.REJECTS in categories:
            self.skills.append(
                punish := Skill(
                    "该罚",
                    SkillType.MISCEL,
                    SkillCategory.REJECTS,
                    require(chaoshen * 2, zan * 1),
                    desc="破除 3 层敌方盾牌。",
                    predicator=self.execute_punish,
                )
            )

            self.skills.append(
                beat2 := Skill(
                    "连拳连脚",
                    SkillType.ATTACK,
                    SkillCategory.REJECTS,
                    require(fangdun * 2, yuandun * 2),
                    damage=4.0,
                )
            )

        if SkillCategory.XIHAI in categories:
            self.skills.append(
                sieg := Skill(
                    "西",
                    SkillType.MISCEL,
                    SkillCategory.XIHAI,
                    require(yuandun * 1, dabi * 1),
                    predicator=self.execute_sieg,
                )
            )

            self.skills.append(
                hai := Skill(
                    "海",
                    SkillType.ATTACK,
                    SkillCategory.XIHAI,
                    require(sieg * 1),
                    damage=2.2,
                )
            )

            self.skills.append(
                rush := Skill(
                    "强袭",
                    SkillType.ATTACK,
                    SkillCategory.XIHAI,
                    require(),
                    predicator=self.execute_rush,
                    extra_check=lambda x: x.hp >= 1.0,
                    damage=2.0,
                )
            )

        if SkillCategory.CCMOD in categories:
            self.skills.append(
                milk := Skill(
                    "米尤克", SkillType.YIELDS, SkillCategory.CCMOD, require()
                )
            )

            self.skills.append(
                milk_producer := Skill(
                    "米尤克 的 小型生产器",
                    SkillType.MISCEL,
                    SkillCategory.CCMOD,
                    require(milk * 2),
                    predicator=lambda x, y: self.execute_duplicator(x, milk, 2, 2),
                    extra_check=lambda x: self.check_duplicator(x, milk, 2),
                )
            )

            self.skills.append(
                milk_duplicator := Skill(
                    "米尤克 的 大型生产器",
                    SkillType.MISCEL,
                    SkillCategory.CCMOD,
                    require(milk * 4),
                    predicator=lambda x, y: self.execute_duplicator(x, milk, 4, 5),
                    extra_check=lambda x: self.check_duplicator(x, milk, 4),
                )
            )

            self.skills.append(
                oo := Skill(
                    "O-O",
                    SkillType.ATTACK,
                    SkillCategory.CCMOD,
                    require(milk * 1),
                    damage=1.0,
                )
            )

            self.skills.append(
                oo2 := Skill(
                    "海普雷",
                    SkillType.ATTACK,
                    SkillCategory.CCMOD,
                    require(milk * 2),
                    damage=2.0,
                )
            )

            self.skills.append(
                oo3 := Skill(
                    "周公巴",
                    SkillType.ATTACK,
                    SkillCategory.CCMOD,
                    require(milk * 3),
                    damage=3.0,
                )
            )

            self.skills.append(
                oo4 := Skill(
                    "迪塞英大炮",
                    SkillType.ATTACK,
                    SkillCategory.CCMOD,
                    require(milk * 4),
                    damage=5.0,
                )
            )

            self.skills.append(
                pax_i := Skill(
                    "绿君之治",
                    SkillType.MISCEL,
                    SkillCategory.CCMOD,
                    require(milk * 9),
                    predicator=self.execute_pax_i,
                )
            )

            self.skills.append(
                pax_ii := Skill(
                    "绿谷之治",
                    SkillType.MISCEL,
                    SkillCategory.CCMOD,
                    require(pax_i * 1),
                    predicator=self.execute_pax_ii,
                )
            )

            self.skills.append(
                cwuzu := Skill(
                    "联合 C 武卒 - 攻下米尤克",
                    SkillType.ATTACK,
                    SkillCategory.CCMOD,
                    require(milk * 15),
                    damage=5.0,
                )
            )

            self.skills.append(
                iran := Skill(
                    "伊朗核竞赛 - C 立行无敌",
                    SkillType.ATTACK,
                    SkillCategory.CCMOD,
                    require(milk * 30),
                    predicator=lambda x, y: x.roundEffect.endure(),
                )
            )

            self.skills.append(
                ayatollah := Skill(
                    "哈梅内伊",
                    SkillType.ATTACK,
                    SkillCategory.CCMOD,
                    require(iran * 1),
                    damage=inf,
                )
            )

        if SkillCategory.JIAYA in categories:
            self.skills.append(
                jiaya := Skill("假牙", SkillType.YIELDS, SkillCategory.JIAYA, require())
            )

            self.skills.append(
                jia1 := Skill(
                    "假牙刀",
                    SkillType.ATTACK,
                    SkillCategory.JIAYA,
                    require(jiaya * 1),
                    damage=1.0,
                )
            )

            self.skills.append(
                jia2 := Skill(
                    "门牙",
                    SkillType.ATTACK,
                    SkillCategory.JIAYA,
                    require(jiaya * 2),
                    damage=2.0,
                )
            )

            self.skills.append(
                jia3 := Skill(
                    "大板牙",
                    SkillType.ATTACK,
                    SkillCategory.JIAYA,
                    require(jiaya * 3),
                    damage=3.0,
                )
            )

            self.skills.append(
                jia4 := Skill(
                    "后槽牙",
                    SkillType.ATTACK,
                    SkillCategory.JIAYA,
                    require(jiaya * 4),
                    damage=4.0,
                )
            )

            self.skills.append(
                jiadun := Skill(
                    "假牙盾",
                    SkillType.SHIELD,
                    SkillCategory.JIAYA,
                    require(jiaya * 10, yuandun * 2),
                    defense=4.0,
                    controlRound=4,
                )
            )

            self.skills.append(
                jiaya_producer := Skill(
                    "假牙 的 小型生产器",
                    SkillType.MISCEL,
                    SkillCategory.JIAYA,
                    require(jiaya * 2),
                    predicator=lambda x, y: self.execute_duplicator(x, jiaya, 2, 2),
                    extra_check=lambda x: self.check_duplicator(x, jiaya, 2),
                )
            )

            self.skills.append(
                jiaya_duplicator := Skill(
                    "假牙 的 大型生产器",
                    SkillType.MISCEL,
                    SkillCategory.JIAYA,
                    require(jiaya * 4),
                    predicator=lambda x, y: self.execute_duplicator(x, jiaya, 4, 5),
                    extra_check=lambda x: self.check_duplicator(x, jiaya, 4),
                )
            )

        if SkillCategory.CCDC in categories:
            self.skills.append(
                lengdun := Skill(
                    "棱盾", SkillType.YIELDS, SkillCategory.CCDC, require(),
                )
            )

            self.skills.append(
                strike := Skill(
                    "肘",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 1),
                    damage=0.9,
                )
            )

            self.skills.append(
                strike2 := Skill(
                    "连肘",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 2),
                    damage=1.8,
                )
            )

            self.skills.append(
                strike3 := Skill(
                    "三连肘",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 3),
                    damage=2.9,
                )
            )

            self.skills.append(
                strike4 := Skill(
                    "重肘",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 4),
                    damage=4.8,
                )
            )

            self.skills.append(
                strike6 := Skill(
                    "肘击连段",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 6),
                    damage=6.5,
                )
            )

            self.skills.append(
                strike8 := Skill(
                    "肘之奥义",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 8),
                    damage=6.0,
                    poisonRound=4,
                )
            )

            self.skills.append(
                zhi := Skill(
                    "掷",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(),
                    damage=0.02,
                    predicator=lambda x, y: x.disable(zhi, waitUntil=2)
                )
            )

            self.skills.append(
                handknife := Skill(
                    "手刃",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 1, dabi * 1),
                    damage=2.3,
                )
            )

            self.skills.append(
                elbowfire := Skill(
                    "肘击炮",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 3, zan * 1),
                    damage=4.8,
                )
            )

            self.skills.append(
                elbowshan := Skill(
                    "肘反",
                    SkillType.MISCEL,
                    SkillCategory.CCDC,
                    require(lengdun * 1),
                    predicator=lambda x, y: x.roundEffect.reduce(3.8),
                )
            )

            self.skills.append(
                furnace := Skill(
                    "锻炉",
                    SkillType.MISCEL,
                    SkillCategory.CCDC,
                    require(lengdun * 3),
                    predicator=lambda x, y: self.execute_furnace(x, fangdun, dabi),
                )
            )

            self.skills.append(
                lengdun_producer := Skill(
                    "棱盾 的 小型生产器",
                    SkillType.MISCEL,
                    SkillCategory.CCDC,
                    require(lengdun * 2),
                    predicator=lambda x, y: self.execute_duplicator(x, lengdun, 2, 2),
                    extra_check=lambda x: self.check_duplicator(x, lengdun, 2),
                )
            )

            self.skills.append(
                lengdun_duplicator := Skill(
                    "棱盾 的 大型生产器",
                    SkillType.MISCEL,
                    SkillCategory.CCDC,
                    require(lengdun * 4),
                    predicator=lambda x, y: self.execute_duplicator(x, lengdun, 4, 5),
                    extra_check=lambda x: self.check_duplicator(x, lengdun, 4),
                )
            )

            self.skills.append(
                combat := Skill(
                    "自由搏击·初",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 1, fangdun * 1, yuandun * 1),
                    damage=3.8,
                )
            )

            self.skills.append(
                combat2 := Skill(
                    "自由搏击·贯",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 2, fangdun * 2, yuandun * 2),
                    damage=8.0,
                )
            )

            self.skills.append(
                combat3 := Skill(
                    "自由搏击·极",
                    SkillType.ATTACK,
                    SkillCategory.CCDC,
                    require(lengdun * 4, fangdun * 4, yuandun * 4),
                    damage=inf,
                )
            )

            self.skills.append(
                slamself := Skill(
                    "重锤（自身）",
                    SkillType.MISCEL,
                    SkillCategory.CCDC,
                    require(zan * 8, dabi * 8),
                    desc="破坏己方全部盾牌并将本回合血量锁定为零。",
                    predicator=lambda x, y: self.execute_slam(x),
                )
            )

            self.skills.append(
                slam := Skill(
                    "重锤",
                    SkillType.MISCEL,
                    SkillCategory.CCDC,
                    require(zan * 8, dabi * 8),
                    desc="破坏对方全部盾牌并将其本回合血量锁定为零。",
                    predicator=lambda x, y: self.execute_slam(y),
                )
            )

            self.skills.append(
                dfire := Skill(
                    "国家消防局",
                    SkillType.SHIELD,
                    SkillCategory.CCDC,
                    require(fangdun * 4),
                    defense=3.2,
                    desc="破碎时，获得2个圆盾",
                    on_break=lambda x, y: self.execute_rescue(x, yuandun * 3),
                )
            )

            self.skills.append(
                dhealth := Skill(
                    "国家卫生局",
                    SkillType.SHIELD,
                    SkillCategory.CCDC,
                    require(yuandun * 4),
                    defense=3.4,
                    desc="破碎时，获得2个攒",
                    on_break=lambda x, y: self.execute_rescue(x, zan * 2),
                )
            )

            self.skills.append(
                dedu := Skill(
                    "国家教育局",
                    SkillType.SHIELD,
                    SkillCategory.CCDC,
                    require(zan * 4),
                    defense=3.2,
                    desc="破碎时，获得2个大臂",
                    on_break=lambda x, y: self.execute_rescue(x, dabi * 2),
                )
            )

            self.skills.append(
                dagri := Skill(
                    "国家农业局",
                    SkillType.SHIELD,
                    SkillCategory.CCDC,
                    require(dabi * 4),
                    defense=3,
                    desc="破碎时，获得2个方盾",
                    on_break=lambda x, y: self.execute_rescue(x, fangdun * 2),
                )
            )

            self.skills.append(
                dphy := Skill(
                    "国家体育局",
                    SkillType.SHIELD,
                    SkillCategory.CCDC,
                    require(lengdun * 1),
                    defense=3.2,
                    desc="破碎时，获得2个棱盾",
                    on_break=lambda x, y: self.execute_rescue(x, lengdun * 2),
                )
            )

            self.skills.append(
                zhoupower := Skill(
                    "肘之力",
                    SkillType.SHIELD,
                    SkillCategory.CCDC,
                    require(lengdun*5),
                    defense=5,
                    controlRound=3
                )
            )

            self.skills.append(
                cannon := Skill(
                    "玻璃大炮",
                    SkillType.MISCEL,
                    SkillCategory.CCDC,
                    require(),
                    predicator=self.execute_cannon,
                    extra_check=lambda x: x.hp >= 1.0,
                )
            )

            self.skills.append(
                ctopia := Skill(
                    "CTOPIA",
                    SkillType.MISCEL,
                    SkillCategory.CCDC,
                    require(dfire*1, dhealth*1, dedu*1, dagri*1, dphy*1),
                    predicator=lambda x, y: x.roundEffect.endure()
                )
            )

            self.skills.append(
                advent := Skill(
                    "降临",
                    SkillType.MISCEL,
                    SkillCategory.CCDC,
                    require(),
                    predicator=self.execute_advent,
                )
            )

            self.skills.append(
                totem := Skill(
                    f"{CSI}33m不死图腾{CSI}0m",
                    SkillType.SHIELD,
                    SkillCategory.CCDC,
                    require(zhoupower*4),
                    on_break=self.execute_pop_totem
                )
            )

        self.dict_skills = locals().copy()
        self.dict_skills.pop("self")

    def execute_totem_save(self, player: Player, opponent: Player):
        if player.hp < 0:
            player.hp = 1

    def defer_remove_save(self, player: Player, opponent: Player):
        player.afterRound.remove(self.execute_totem_save)

    def execute_pop_totem(self, player: Player, opponent: Player):
        player.afterRound.append(self.execute_totem_save)
        player.defer.append(self.defer_remove_save)

    def execute_advent(self, player: Player, opponent: Player):
        player.roundEffect.endure()
        opponent.hp = -inf # FORCE KILL

    def execute_protect_from(self, player: Player, opponent: Player, *skills: Skill):
        if opponent.skillPlayed is None:
            return
        
        if any(
            opponent.skillPlayed.requirement.includes(skill.id) or skill == opponent.skillPlayed
            for skill in skills
        ):
            player.roundEffect.reduce(1)

    def execute_disable_attack(self, player: Player, opponent: Player):
        attacks = []
        for skill in self.skills:
            if skill.type == SkillType.ATTACK:
                attacks.append(skill)
    
        player.disable(*attacks)

    def execute_furnace(self, player: Player, fangdun: Skill, dabi: Skill):
        player.resources.setdefault(fangdun.id, 0)
        player.resources.setdefault(dabi.id, 0)
        player.resources[fangdun.id] += 2
        player.resources[dabi.id] += 1

    def cannon_beforeSettle(self, remote: Player, local: Player):
        if 0.5 < remote.roundEffect.damageTaken < 5:
            remote.roundEffect.damageTaken += 1
        elif remote.roundEffect.damageTaken >= 5:
            remote.roundEffect.damageTaken += 2

    def execute_cannon(self, player: Player, opponent: Player):
        player.hp -= 1.0
        opponent.beforeSettle.append(self.cannon_beforeSettle)

    def execute_rescue(self, player: Player, save: tuple[int, int]):
        player.resources.setdefault(save[0], 0)
        player.resources[save[0]] += save[1]

    def execute_punish(self, player: Player, opponent: Player):
        i = 3
        while len(opponent.shields) > 0 and i > 0:
            i -= 1
            opponent.shields.pop()

    def execute_sieg(self, player: Player, opponent: Player):
        player.hp = 1.0

    def execute_duplicator(
        self, player: Player, skill: Skill, originCount: int, increaseCount: int
    ):
        player.resources.setdefault(skill.id, 0)
        player.duplicatedResources.setdefault(skill.id, 0)

        player.resources[skill.id] += originCount + increaseCount
        player.duplicatedResources[skill.id] += originCount + increaseCount

    def check_duplicator(self, player: Player, skill: Skill, needsClean: int):
        player.resources.setdefault(skill.id, 0)
        player.duplicatedResources.setdefault(skill.id, 0)

        return (
            player.resources[skill.id] - player.duplicatedResources[skill.id]
            >= needsClean
        )

    def execute_rush(self, player: Player, opponent: Player):
        player.hp -= 1.0

    def execute_pax_i(self, player: Player, opponent: Player):
        player.hp += 3.0

    def execute_pax_ii(self, player: Player, opponent: Player):
        player.hp += 2.0

    def execute_slam(self, player: Player):
        player.hp = 0
        player.shields.clear()
        player.roundEffect.damageTaken -= inf * inf

    def isSkillAvailable(self, player: Player, skill: Skill):
        return player.isValidPlay(skill) and skill.extra_check(player)

    def chooseLocalAction(self, n: int) -> RoundAction:
        system("cls")

        availableSkills = [
            s for s in self.skills if self.isSkillAvailable(self.localPlayer, s)
        ]
        if not availableSkills:
            print("【提示】本回合，你无可用技能。")
            return RoundAction(SkillType.NOP, -1)
        if self.localPlayer.roundsControlled > 0:
            print("=" * 10, f"第 {n} 回合 选择", "=" * 10)
            print(
                f"【被控】此回合你被控制，无法进行操作。剩余控制 {self.localPlayer.roundsControlled} 回合。"
            )
            return RoundAction(SkillType.NOP, -1)

        selected = self.ui.chooseAction(n, availableSkills)
        skill = self.skills[selected]

        self.localPlayer.disabled.clear()

        return RoundAction(skill.type, selected)

    def executeSkill(self, sub: Player, ob: Player, skill: Skill):
        sub.consumeResource(skill.requirement)
        skill.predicator(sub, ob)

        if skill.disableSelf:
            sub.disable(skill)
        
        ob.roundEffect.register(skill)
        sub.resources.setdefault(skill.id, 0)
        sub.resources[skill.id] += 1

        ob.poisonRemaining += skill.poisonRound
        if skill.poisonRound:
            print(f"【中毒】{ob.name}被感染，增加 {skill.poisonRound} 中毒回合。")

    def settleRound(
        self, n: int, lSkill: Optional[Skill] = None, rSkill: Optional[Skill] = None
    ) -> bool:
        # 清除上回合伤害状态
        self.localPlayer.roundEffect.clear()
        self.remotePlayer.roundEffect.clear()

        self.localPlayer.roundsControlled = max(
            self.localPlayer.roundsControlled - 1, 0
        )
        self.remotePlayer.roundsControlled = max(
            self.remotePlayer.roundsControlled - 1, 0
        )

        system("cls")
        print("=" * 10, f"第 {n} 回合", "=" * 10)
        if lSkill is None:
            print(f"{CSI}92m我方 {CSI}0m{self.localPlayer.name} 的抉择：无")
        else:
            print(f"{CSI}92m我方 {CSI}0m{self.localPlayer.name} 的抉择：{lSkill.name}")
        
        if rSkill is None:
            print(f"{CSI}91m对方 {CSI}0m{self.remotePlayer.name} 的抉择：无")
        else:
            print(f"{CSI}91m对方 {CSI}0m{self.remotePlayer.name} 的抉择：{rSkill.name}")

        for f in self.localPlayer.defer:
            f(self.localPlayer, self.remotePlayer)
        
        for f in self.remotePlayer.defer:
            f(self.remotePlayer, self.localPlayer)

        self.localPlayer.defer.clear()
        self.remotePlayer.defer.clear()

        for f in self.localPlayer.beforeRound:
            f(self.localPlayer, self.remotePlayer)

        for f in self.remotePlayer.beforeRound:
            f(self.remotePlayer, self.localPlayer)

        # 处理中毒和延迟操作
        self.localPlayer.applyPoison()
        self.remotePlayer.applyPoison()

        self.localPlayer.skillPlayed = lSkill
        self.remotePlayer.skillPlayed = rSkill

        # 执行技能效果，结算伤害
        if lSkill is not None:
            self.executeSkill(self.localPlayer, self.remotePlayer, lSkill)

        if rSkill is not None:
            self.executeSkill(self.remotePlayer, self.localPlayer, rSkill)

        for f in self.localPlayer.beforeSettle:
            f(self.localPlayer, self.remotePlayer)

        for f in self.remotePlayer.beforeSettle:
            f(self.remotePlayer, self.localPlayer)

        self.localPlayer.roundEffect.offset(self.remotePlayer.roundEffect)

        # 结算盾牌状态（被控将不会受到伤害）
        if lSkill is not None:
            self.remotePlayer.roundsControlled += self.localPlayer.takeDamage(
                self.remotePlayer,
            )
        else:
            print(f"{self.localPlayer.name} 被控制，免疫伤害！")

        if rSkill is not None:
            self.localPlayer.roundsControlled += self.remotePlayer.takeDamage(
                self.localPlayer,
            )
        else:
            print(f"{self.remotePlayer.name} 被控制，免疫伤害！")

        # 结算回合结束
        for f in self.localPlayer.afterRound:
            f(self.localPlayer, self.remotePlayer)

        for f in self.remotePlayer.afterRound:
            f(self.remotePlayer, self.localPlayer)

        if self.localPlayer.hp < 0:
            print(f"{CSI}31m结算 {CSI}0m{self.localPlayer.name} 阵亡！")
            print(f"{CSI}31m你输了！{CSI}0m")
            return False

        if self.remotePlayer.hp < 0:
            print(f"{CSI}32m结算 {CSI}0m{self.remotePlayer.name} 阵亡！")
            print(f"{CSI}32m你赢了！{CSI}0m")
            return False

        return True  # 游戏继续

    def round(self, n: int) -> bool:
        local_action = self.chooseLocalAction(n)
        print("等待对手操作...")
        try:
            self.sock.send(local_action.pack())
        except Exception:
            print(f"{CSI}31m错误 {CSI}0m连接断开，游戏结束。")
            return False

        try:
            remote_action = self.sock.recv(32)
        except socket.error:
            print(f"{CSI}31m错误 {CSI}[0m连接断开，游戏结束。")
            return False

        remote_action = RoundAction.unpack(remote_action)
        lSkill = (
            None
            if local_action.actionType == SkillType.NOP
            else self.skills[local_action.skillId]
        )
        rSkill = (
            None
            if remote_action.actionType == SkillType.NOP
            else self.skills[remote_action.skillId]
        )

        return self.settleRound(n, lSkill, rSkill)

    def guardian(self) -> bool:
        src = (
            inspect.getsource(Player)
            + inspect.getsource(Skill)
            + inspect.getsource(Requirement)
            + inspect.getsource(Game)
            + inspect.getsource(UserInterface)
        )
        self.sock.send(local_hash := hashlib.sha256(src.encode()).digest())
        remote_hash = self.sock.recv(512)
        if local_hash != remote_hash:
            print(
                b"\x1b[90m[\x1b[31mCC \x1b[33mGame\x1b[90m-\x1b[32mGuard\x1b[90m]\x1b[31m \xe6\xa3\x80\xe6\xb5\x8b\xe5\x88\xb0\xe4\xbd\x9c\xe5\xbc\x8a\xe8\xa1\x8c\xe4\xb8\xba\xef\xbc\x8c\xe5\xb7\xb2\xe5\x8f\x8a\xe6\x97\xb6\xe5\x88\xb6\xe6\xad\xa2\x1b[0m".decode(
                    "utf-8"
                )
            )
            return False
        return True

    def findOnlineRooms(self) -> list[tuple[str, dict]]:
        B192 = ipaddress.ip_network("192.168.3.0/24")
        C172 = ipaddress.ip_network("172.17.43.0/24")
        IPS = list(itertools.chain(C172.hosts(), B192.hosts()))

        rooms: list[tuple[str, dict]] = []

        system("cls")
        print("=" * 10, VERSION, "- 寻找游戏", "=" * 10)
        print()
        for i, ip in enumerate(IPS):
            with contextlib.suppress(socket.error):
                print(
                    f"{CSI}F{CSI}K正在尝试连接 {ip} {CSI}90m({CSI}92m{i}{CSI}90m/{CSI}93m{len(IPS)}{CSI}90m) - {CSI}92m{round(i / len(IPS) * 100, 2)}%{CSI}90m){CSI}0m ..."
                )
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.01)
                if sock.connect_ex((str(ip), PORT)) == 0:  # 端口开放
                    sock.send(b"CCDABI_GUEST_REQUEST_INFO")
                    info = sock.recv(1024).decode()
                    rooms.append((str(ip), json.loads(info)))
                    sock.close()
        return rooms

    def init(self) -> bool:
        hostGuest, self.localPlayer.name, ip = self.ui.chooseHostGuest(
            self.findOnlineRooms
        )
        if hostGuest == 0:
            if not self.asHost():
                return False
        else:
            if not self.asGuest(ip):
                return False

        print("正在初始化游戏...")
        self.initSkills(*self.suits)
        print("同步玩家信息...")
        if not self.syncPlayerInfo():
            return False

        return True

    def start(self):
        round_num = 1

        while self.gameReady:
            self.gameReady = self.round(round_num)
            round_num += 1

            if self.gameReady:
                self.ui.tryShowMaterials(round_num, self.localPlayer, self.remotePlayer)

        self.sock.close()

    def run(self):
        if not self.init() or not self.gameReady:
            print("游戏初始化失败！")
            return
        self.start()
        print("=" * 3, "按任意键回到主菜单", "=" * 3)
        msvcrt.getch()


if __name__ == "__main__":
    while True:
        game = Game()
        game.run()
