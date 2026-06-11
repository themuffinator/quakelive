from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
CGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "functions.csv"
)
CGAME_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "cgamex86.dll" / "cgamex86.dll_hlil.txt"


def _block_from_marker(source: str, marker: str) -> str:
	start = source.rindex(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def _function_rows() -> dict[str, dict[str, str]]:
	return {
		row["entry"].lower(): row
		for row in csv.DictReader(CGAME_FUNCTIONS.read_text(encoding="utf-8").splitlines())
	}


def test_cgame_register_sounds_alias_and_hlil_cover_retail_registration_slice() -> None:
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["cgame"]
	rows = _function_rows()
	hlil = CGAME_HLIL.read_text(encoding="utf-8")

	assert aliases["FUN_10020e70"] == "CG_RegisterSounds"
	assert aliases["sub_10020e70"] == "CG_RegisterSounds"
	assert rows["10020e70"]["name"] == "FUN_10020e70"
	assert rows["10020e70"]["size"] == "8324"

	for expected in (
		"10020e70    int32_t sub_10020e70()",
		"10021141      int32_t eax_51 = (*(data_1074cccc + 0xb8))(\"sound/feedback/hit_teammate.ogg\")",
		"10021159      int32_t eax_53 = (*(edx_11 + 0xb8))(\"sound/teamplay/flagreturn_yourte",
		"1002118f      int32_t eax_57 = (*(esi_14 + 0xb8))(sub_10020dd0(\"prepare_your_team.ogg\"))",
		"100211ad      int32_t eax_59 = (*(esi_15 + 0xb8))(sub_10020dd0(\"red_leads.ogg\"))",
		"100211cb      int32_t eax_61 = (*(esi_16 + 0xb8))(sub_10020dd0(\"blue_leads.ogg\"))",
		"100211e9      int32_t eax_64 = (*(esi_17 + 0xb8))(sub_10020dd0(\"teams_tied.ogg\"))",
		"10021207      int32_t eax_66 = (*(esi_18 + 0xb8))(sub_10020dd0(\"red_scores.ogg\"))",
		"10021225      int32_t eax_68 = (*(esi_19 + 0xb8))(sub_10020dd0(\"blue_scores.ogg\"))",
		"10021681                      (*(esi_42 + 0xb8))(sub_10020dd0(\"blue_flag_returned.ogg\"))",
		"100216bd                      (*(esi_44 + 0xb8))(sub_10020dd0(\"red_flag_returned.ogg\"))",
		"10021756                      (*(esi_49 + 0xb8))(sub_10020dd0(\"the_enemy_has_flag.ogg\"))",
		"10021776                  data_10a5fb04 = (*(esi_50 + 0xb8))(sub_10020dd0(\"your_team_has_flag.ogg\"))",
		"100217a9                      (*(data_1074cccc + 0xb8))(sub_10020dd0(\"you_have_flag.ogg\"))",
		"100217c9                  data_10a5fb10 = (*(esi_52 + 0xb8))(sub_10020dd0(\"holy_shit.ogg\"))",
		"10021857                  data_10a5fb0c = (*(esi_53 + 0xb8))(sub_10020dd0(\"base_attack.ogg\"))",
		"10021880                      (*(data_1074cccc + 0xb8))(sub_10020dd0(\"attack_the_flag.ogg\"))",
		"100218a0                  data_10a5fb50 = (*(esi_55 + 0xb8))(sub_10020dd0(\"defend_the_flag.ogg\"))",
		"10021963  data_10a5f800 = (*(ecx_45 + 0xb8))(\"sound/items/wearoff.ogg\")",
		"10022158  int32_t eax_342 = (*(esi_91 + 0xb8))(sub_10020dd0(\"lead_taken.ogg\"))",
		"10022179  int32_t eax_344 = (*(esi_92 + 0xb8))(sub_10020dd0(\"lead_tied.ogg\"))",
		"10022197  int32_t eax_346 = (*(esi_93 + 0xb8))(sub_10020dd0(\"lead_lost.ogg\"))",
		"100221b5  int32_t eax_349 = (*(esi_94 + 0xb8))(sub_10020dd0(\"vote_now.ogg\"))",
		"100221d3  int32_t eax_351 = (*(esi_95 + 0xb8))(sub_10020dd0(\"vote_passed.ogg\"))",
		"100221f1  int32_t eax_353 = (*(esi_96 + 0xb8))(sub_10020dd0(\"vote_failed.ogg\"))",
		"1002220f  int32_t eax_356 = (*(esi_97 + 0xb8))(sub_10020dd0(\"you_win.ogg\"))",
		"10022237  data_10a5f908 = (*(esi_98 + 0xb8))(sub_10020dd0(\"you_lose.ogg\"))",
		"10022507  char const* const var_498_13 = \"battlesuit.ogg\"",
		"1002277d  char const* const var_498_16 = \"quad_damage.ogg\"",
		"10022bdb  int32_t eax_464 = (*(data_1074cccc + 0xb8))(\"sound/items/flight.ogg\")",
		"10022bf3  int32_t eax_466 = (*(edx_128 + 0xb8))(\"sound/items/use_medkit.ogg\")",
		"10022c0d  data_10a5f7f0 = (*(ecx_132 + 0xb8))(\"sound/items/damage3.ogg\")",
		"10022d88  int32_t eax_494 = (*(data_1074cccc + 0xb8))(\"sound/items/kam_explode.ogg\")",
		"10022da0  int32_t eax_496 = (*(edx_140 + 0xb8))(\"sound/items/kam_implode.ogg\")",
		"10022dba  data_10a5f8e0 = (*(ecx_144 + 0xb8))(\"sound/items/kam_explode_far.ogg\")",
		"10022dcf  int32_t eax_499 = (*(data_1074cccc + 0xb8))(\"sound/misc/yousuck.ogg\")",
	):
		assert expected in hlil


def test_cgame_register_sounds_restores_retail_weapon_and_item_effect_ogg_paths() -> None:
	source = CG_MAIN.read_text( encoding = "utf-8" )

	for expected in (
		'"sound/weapons/machinegun/buletby1.ogg"',
		'"sound/weapons/change.ogg"',
		'"sound/items/wearoff.ogg"',
		'"sound/items/use_nothing.ogg"',
		'"sound/items/obelisk_hit_01.ogg"',
		'"sound/items/obelisk_hit_02.ogg"',
		'"sound/items/obelisk_hit_03.ogg"',
		'"sound/items/obelisk_respawn.ogg"',
		'"sound/items/flight.ogg"',
		'"sound/items/use_medkit.ogg"',
		'"sound/items/damage3.ogg"',
		'"sound/items/kam_explode.ogg"',
		'"sound/items/kam_implode.ogg"',
		'"sound/items/kam_explode_far.ogg"',
		'"sound/misc/yousuck.ogg"',
		'"sound/items/regen.ogg"',
		'"sound/items/protect3.ogg"',
		'"sound/items/n_health.ogg"',
		'"sound/weapons/grenade/hgrenb1a.ogg"',
		'"sound/weapons/grenade/hgrenb2a.ogg"',
	):
		assert expected in source

	for legacy in (
		'"sound/weapons/machinegun/buletby1.wav"',
		'"sound/weapons/change.wav"',
		'"sound/items/wearoff.wav"',
		'"sound/items/use_nothing.wav"',
		'"sound/items/obelisk_hit_01.wav"',
		'"sound/items/obelisk_hit_02.wav"',
		'"sound/items/obelisk_hit_03.wav"',
		'"sound/items/obelisk_respawn.wav"',
		'"sound/items/flight.wav"',
		'"sound/items/use_medkit.wav"',
		'"sound/items/damage3.wav"',
		'"sound/items/kam_explode.wav"',
		'"sound/items/kam_implode.wav"',
		'"sound/items/kam_explode_far.wav"',
		'"sound/misc/yousuck.wav"',
		'"sound/items/regen.wav"',
		'"sound/items/protect3.wav"',
		'"sound/items/n_health.wav"',
		'"sound/weapons/grenade/hgrenb1a.wav"',
		'"sound/weapons/grenade/hgrenb2a.wav"',
	):
		assert legacy not in source


def test_cgame_register_sounds_restores_retail_teamplay_announcer_and_direct_sound_slice() -> None:
	source = CG_MAIN.read_text( encoding = "utf-8" )
	helper_block = _block_from_marker( source, "static sfxHandle_t CG_RegisterConfiguredAnnouncerClip" )
	powerup_voice_block = _block_from_marker( source, "static void CG_RegisterPowerupAnnouncerSounds" )

	for expected in (
		'path = CG_BuildAnnouncerSoundPath( sample );',
		'return trap_S_RegisterSound( path, qtrue );',
	):
		assert expected in helper_block

	assert "#define CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE(field, retailSample) \\" in source

	for expected in (
		'cgs.media.countPrepareTeamSound = 0;',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( countPrepareTeamSound, "prepare_your_team.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( redLeadsSound, "red_leads.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( blueLeadsSound, "blue_leads.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( teamsTiedSound, "teams_tied.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( redScoredSound, "red_scores.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( blueScoredSound, "blue_scores.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( redFlagReturnedSound, "red_flag_returned.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( blueFlagReturnedSound, "blue_flag_returned.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( enemyTookYourFlagSound, "the_enemy_has_flag.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( yourTeamTookEnemyFlagSound, "your_team_has_flag.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( yourTeamTookTheFlagSound, "attack_the_flag.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( enemyTookTheFlagSound, "defend_the_flag.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( youHaveFlagSound, "you_have_flag.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( holyShitSound, "holy_shit.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( yourBaseIsUnderAttackSound, "base_attack.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( takenLeadSound, "lead_taken.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( tiedLeadSound, "lead_tied.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( lostLeadSound, "lead_lost.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( voteNow, "vote_now.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( votePassed, "vote_passed.ogg" );',
		'CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( voteFailed, "vote_failed.ogg" );',
		'cgs.media.winnerSound = CG_RegisterConfiguredAnnouncerClip( "you_win.ogg" );',
		'cgs.media.loserSound = CG_RegisterConfiguredAnnouncerClip( "you_lose.ogg" );',
		'cgs.media.captureAwardSound = trap_S_RegisterSound( "sound/teamplay/flagcapture_yourteam.ogg", qtrue );',
		'cgs.media.hitTeamSound = trap_S_RegisterSound( "sound/feedback/hit_teammate.ogg", qtrue );',
		'cgs.media.captureYourTeamSound = trap_S_RegisterSound( "sound/teamplay/flagcapture_yourteam.ogg", qtrue );',
		'cgs.media.captureOpponentSound = trap_S_RegisterSound( "sound/teamplay/flagcapture_opponent.ogg", qtrue );',
		'cgs.media.returnYourTeamSound = trap_S_RegisterSound( "sound/teamplay/flagreturn_yourteam.ogg", qtrue );',
		'cgs.media.returnOpponentSound = trap_S_RegisterSound( "sound/teamplay/flagreturn_opponent.ogg", qtrue );',
		'cgs.media.takenYourTeamSound = trap_S_RegisterSound( "sound/teamplay/flagtaken_yourteam.ogg", qtrue );',
		'cgs.media.takenOpponentSound = trap_S_RegisterSound( "sound/teamplay/flagtaken_opponent.ogg", qtrue );',
		'cgs.media.neutralFlagReturnedSound = trap_S_RegisterSound( "sound/teamplay/flagreturn_opponent.ogg", qtrue );',
	):
		assert expected in source

	for expected in (
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( battleSuitPowerupSound, "battlesuit.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( hastePowerupSound, "haste.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( invisibilityPowerupSound, "invisibility.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( quadDamagePowerupSound, "quad_damage.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( regenerationPowerupSound, "regeneration.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( armorRegenPowerupSound, "armor_regen.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( damagePowerupSound, "damage.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( guardPowerupSound, "guard.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( scoutPowerupSound, "scout.ogg" );',
	):
		assert expected in powerup_voice_block

	assert "CG_RegisterPowerupAnnouncerSounds();" in _block_from_marker(
		source, "static void CG_UpdateAnnouncerProfileFromCvar"
	)

	for legacy in (
		'"sound/feedback/prepare_team.wav"',
		'"sound/feedback/redleads.wav"',
		'"sound/feedback/blueleads.wav"',
		'"sound/feedback/teamstied.wav"',
		'"sound/feedback/hit_teammate.wav"',
		'"sound/teamplay/voc_red_scores.wav"',
		'"sound/teamplay/voc_blue_scores.wav"',
		'"sound/teamplay/flagcapture_yourteam.wav"',
		'"sound/teamplay/flagcapture_opponent.wav"',
		'"sound/teamplay/flagreturn_yourteam.wav"',
		'"sound/teamplay/flagreturn_opponent.wav"',
		'"sound/teamplay/flagtaken_yourteam.wav"',
		'"sound/teamplay/flagtaken_opponent.wav"',
		'"sound/teamplay/voc_red_returned.wav"',
		'"sound/teamplay/voc_blue_returned.wav"',
		'"sound/teamplay/voc_enemy_flag.wav"',
		'"sound/teamplay/voc_team_flag.wav"',
		'"sound/teamplay/voc_team_1flag.wav"',
		'"sound/teamplay/voc_enemy_1flag.wav"',
		'"sound/teamplay/voc_you_flag.wav"',
		'"sound/feedback/voc_holyshit.wav"',
		'"sound/teamplay/voc_base_attack.wav"',
		'"sound/feedback/takenlead.wav"',
		'"sound/feedback/tiedlead.wav"',
		'"sound/feedback/lostlead.wav"',
		'"sound/feedback/vote_now.wav"',
		'"sound/feedback/vote_passed.wav"',
		'"sound/feedback/vote_failed.wav"',
		'"sound/feedback/voc_youwin.wav"',
		'"sound/feedback/voc_youlose.wav"',
	):
		assert legacy not in source
