/*
===========================================================================
Copyright (C) 1999-2005 Id Software, Inc.

This file is part of Quake III Arena source code.

Quake III Arena source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake III Arena source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
*/
//

#include "g_local.h"
#include "g_team.h"

/*
=============
SP_team_dom_point

Spawns a Domination capture trigger volume.
=============
*/
void SP_team_dom_point( gentity_t *ent ) {
	if ( g_gametype.integer != GT_DOMINATION ) {
		G_FreeEntity( ent );
		return;
	}

	if ( !ent->model || !ent->model[0] ) {
		G_Printf( "SP_team_dom_point: missing model\n" );
		G_FreeEntity( ent );
		return;
	}

	trap_SetBrushModel( ent, ent->model );
	InitTrigger( ent );

	ent->touch = Team_DominationPointTouch;
	ent->r.svFlags |= SVF_NOCLIENT;

	Team_RegisterDominationPoint( ent, ent->message );
}
