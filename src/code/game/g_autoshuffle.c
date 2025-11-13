#include "g_local.h"

static qboolean ( *g_autoShuffleCountdownGuard )( void ) = NULL;

/*
=============
G_AutoShuffleCountdown_SetGuard

Registers a guard callback used to defer auto-shuffle announcements when the
backend or game flow requests it.
=============
*/
void G_AutoShuffleCountdown_SetGuard( qboolean ( *guard )( void ) )
{
	g_autoShuffleCountdownGuard = guard;
}

/*
=============
G_AutoShuffleCountdown_Arm

Arms the auto-shuffle countdown for the supplied duration in milliseconds.
=============
*/
void G_AutoShuffleCountdown_Arm( int milliseconds )
{
	if ( milliseconds <= 0 ) {
		level.autoShuffleCountdownActive = qfalse;
		level.autoShuffleCountdownTargetTime = level.time;
		level.autoShuffleCountdownLastAnnounce = -1;
		return;
	}

	level.autoShuffleCountdownActive = qtrue;
	level.autoShuffleCountdownTargetTime = level.time + milliseconds;
	level.autoShuffleCountdownLastAnnounce = -1;
}

/*
=============
G_AutoShuffleCountdown_Cancel

Cancels any pending auto-shuffle countdown.
=============
*/
void G_AutoShuffleCountdown_Cancel( void )
{
	level.autoShuffleCountdownActive = qfalse;
	level.autoShuffleCountdownTargetTime = 0;
	level.autoShuffleCountdownLastAnnounce = -1;
}

/*
=============
G_AutoShuffleCountdown_IsActive

Reports whether an auto-shuffle countdown is currently armed.
=============
*/
qboolean G_AutoShuffleCountdown_IsActive( void )
{
	return level.autoShuffleCountdownActive;
}

/*
=============
G_AutoShuffleCountdown_GetSecondsRemaining

Returns the rounded-up number of whole seconds remaining on the countdown.
=============
*/
int G_AutoShuffleCountdown_GetSecondsRemaining( void )
{
	if ( !level.autoShuffleCountdownActive ) {
		return 0;
	}

	const int remainingMillis = level.autoShuffleCountdownTargetTime - level.time;
	if ( remainingMillis <= 0 ) {
		return 0;
	}

	return ( remainingMillis + 999 ) / 1000;
}

/*
=============
G_AutoShuffleCountdown_Frame

Processes the armed countdown, emitting announcements as whole seconds tick
away while respecting intermission and backend guard states.
=============
*/
void G_AutoShuffleCountdown_Frame( void )
{
	if ( !level.autoShuffleCountdownActive ) {
		return;
	}

	const int remainingMillis = level.autoShuffleCountdownTargetTime - level.time;
	if ( remainingMillis <= 0 ) {
		level.autoShuffleCountdownActive = qfalse;
		level.autoShuffleCountdownTargetTime = 0;
		level.autoShuffleCountdownLastAnnounce = -1;
		return;
	}

	const int secondsRemaining = ( remainingMillis + 999 ) / 1000;
	if ( secondsRemaining <= 0 ) {
		return;
	}

	qboolean defer = qfalse;
	if ( level.intermissionQueued || level.intermissiontime ) {
		defer = qtrue;
	}
	if ( level.timeoutActive ) {
		defer = qtrue;
	}
	if ( g_autoShuffleCountdownGuard && g_autoShuffleCountdownGuard() ) {
		defer = qtrue;
	}

	if ( defer ) {
		return;
	}

	if ( secondsRemaining == level.autoShuffleCountdownLastAnnounce ) {
		return;
	}

	level.autoShuffleCountdownLastAnnounce = secondsRemaining;
	trap_SendServerCommand( -1, va( "cp \"Auto-Shuffling Teams in %d seconds.\\n\"", secondsRemaining ) );
}
