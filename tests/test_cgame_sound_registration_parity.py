from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"


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
