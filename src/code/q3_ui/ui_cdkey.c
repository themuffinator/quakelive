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
/*
=======================================================================

CD KEY MENU

=======================================================================
*/


#include "ui_local.h"
#include <ctype.h>


#define ART_FRAME		"menu/art/cut_frame"
#define ART_ACCEPT0		"menu/art/accept_0"
#define ART_ACCEPT1		"menu/art/accept_1"	
#define ART_BACK0		"menu/art/back_0"
#define ART_BACK1		"menu/art/back_1"	

#define ID_TYPE		10
#define ID_ACCEPT		11
#define ID_BACK			12

#define MAX_CREDENTIAL_CHARS	128

typedef enum {
	UI_CREDENTIAL_KIND_LEGACY = 0,
	UI_CREDENTIAL_KIND_STEAM,
	UI_CREDENTIAL_KIND_STANDALONE,
	UI_CREDENTIAL_KIND_COUNT
} uiCredentialKind_t;

static const char *const uiCredentialKindNames[UI_CREDENTIAL_KIND_COUNT + 1] = {
	"Legacy CD Key",
	"Steam Ticket",
	"Standalone Token",
	NULL
};

static const char *const uiCredentialKindPrompts[UI_CREDENTIAL_KIND_COUNT] = {
	"Enter the 16-character key from your retail copy.",
	"Paste the Steam session ticket provided by the platform.",
	"Paste the launcher-issued standalone token for this device."
};

static const char *const uiCredentialKindSuccess[UI_CREDENTIAL_KIND_COUNT] = {
	"Key format looks valid. Save to apply.",
	"Token captured. Save to apply.",
	"Token captured. Save to apply."
};

static const char *const uiCredentialKindErrors[UI_CREDENTIAL_KIND_COUNT] = {
	"Key must contain 16 valid characters (no spaces or dashes).",
	"Token cannot be blank.",
	"Token cannot be blank."
};

static const char *const uiCredentialAutoMessages[UI_CREDENTIAL_KIND_COUNT] = {
	"This credential is managed manually.",
	"Steam credentials are provisioned automatically while this build is linked to Steam.",
	"Standalone launcher tokens are provisioned automatically for this installation."
};

static const char *const uiCredentialKindPrefixes[UI_CREDENTIAL_KIND_COUNT] = {
	"",
	"steam:",
	"standalone:"
};


typedef struct {
	menuframework_s menu;

	menutext_s		banner;
	menubitmap_s	frame;
	menulist_s		type;
	menufield_s		cdkey;

	menubitmap_s	accept;
	menubitmap_s	back;
	qboolean		autoProvisioned;
	int			credentialKind;
} cdkeyMenuInfo_t;

static cdkeyMenuInfo_t	cdkeyMenuInfo;

static void UI_CDKeyMenu_StripWhitespace( char *out, size_t outSize, const char *in ) {
	char *dst;

	if ( !out || !outSize ) {
		return;
	}

	dst = out;
	*dst = '\0';

	if ( !in ) {
		return;
	}

	while ( *in && (size_t)( dst - out ) + 1 < outSize ) {
		if ( !isspace( (unsigned char)*in ) ) {
			*dst++ = *in;
		}
		in++;
	}

	*dst = '\0';
}

static int UI_CDKeyMenu_ParseCredentialKind( const char *value ) {
	if ( !value || !value[0] ) {
		return UI_CREDENTIAL_KIND_LEGACY;
	}

	if ( !Q_strnicmp( value, uiCredentialKindPrefixes[UI_CREDENTIAL_KIND_STEAM], strlen( uiCredentialKindPrefixes[UI_CREDENTIAL_KIND_STEAM] ) ) ) {
		return UI_CREDENTIAL_KIND_STEAM;
	}

	if ( !Q_strnicmp( value, uiCredentialKindPrefixes[UI_CREDENTIAL_KIND_STANDALONE], strlen( uiCredentialKindPrefixes[UI_CREDENTIAL_KIND_STANDALONE] ) ) ) {
		return UI_CREDENTIAL_KIND_STANDALONE;
	}

	return UI_CREDENTIAL_KIND_LEGACY;
}

static void UI_CDKeyMenu_CopyCredentialToField( const char *value, int kind ) {
	const char *source = value ? value : "";
	size_t prefixLength;

	if ( kind == UI_CREDENTIAL_KIND_STEAM || kind == UI_CREDENTIAL_KIND_STANDALONE ) {
		prefixLength = strlen( uiCredentialKindPrefixes[kind] );
		if ( !Q_strnicmp( source, uiCredentialKindPrefixes[kind], prefixLength ) ) {
			source += prefixLength;
		}
	}

	Q_strncpyz( cdkeyMenuInfo.cdkey.field.buffer, source, cdkeyMenuInfo.cdkey.field.maxchars + 1 );
	cdkeyMenuInfo.cdkey.field.cursor = strlen( cdkeyMenuInfo.cdkey.field.buffer );
	cdkeyMenuInfo.cdkey.field.scroll = 0;
}

static void UI_CDKeyMenu_UpdateVisibility( void ) {
	if ( cdkeyMenuInfo.autoProvisioned ) {
		cdkeyMenuInfo.cdkey.generic.flags |= ( QMF_HIDDEN | QMF_INACTIVE );
		cdkeyMenuInfo.type.generic.flags |= ( QMF_GRAYED | QMF_INACTIVE );
	} else {
		cdkeyMenuInfo.cdkey.generic.flags &= ~( QMF_HIDDEN | QMF_INACTIVE );
		cdkeyMenuInfo.type.generic.flags &= ~( QMF_GRAYED | QMF_INACTIVE );
	}
}

static void UI_CDKeyMenu_FormatCredential( char *out, size_t outSize, const char *sanitized, int kind ) {
	if ( !out || !outSize ) {
		return;
	}

	if ( kind == UI_CREDENTIAL_KIND_LEGACY ) {
		Q_strncpyz( out, sanitized ? sanitized : "", outSize );
		Q_strupr( out );
	} else {
		Com_sprintf( out, outSize, "%s%s", uiCredentialKindPrefixes[kind], sanitized ? sanitized : "" );
	}
}


/*
===============
UI_CDKeyMenu_Event
===============
*/
static void UI_CDKeyMenu_Event( void *ptr, int event ) {
	menucommon_s *item;
	char sanitized[MAX_EDIT_LINE];
	char formatted[MAX_EDIT_LINE];
	int validation;

	if ( event != QM_ACTIVATED ) {
		return;
	}

	item = (menucommon_s *)ptr;

	switch ( item->id ) {
	case ID_ACCEPT:
		if ( cdkeyMenuInfo.autoProvisioned ) {
			UI_PopMenu();
			break;
		}

		UI_CDKeyMenu_StripWhitespace( sanitized, sizeof( sanitized ), cdkeyMenuInfo.cdkey.field.buffer );
		validation = UI_CDKeyMenu_PreValidateKey( sanitized );
		if ( validation != 0 ) {
			break;
		}

		UI_CDKeyMenu_FormatCredential( formatted, sizeof( formatted ), sanitized, cdkeyMenuInfo.credentialKind );
		trap_SetCDKey( formatted );

		if ( cdkeyMenuInfo.credentialKind == UI_CREDENTIAL_KIND_LEGACY ) {
			Q_strncpyz( cdkeyMenuInfo.cdkey.field.buffer, sanitized, cdkeyMenuInfo.cdkey.field.maxchars + 1 );
			Q_strupr( cdkeyMenuInfo.cdkey.field.buffer );
		} else {
			Q_strncpyz( cdkeyMenuInfo.cdkey.field.buffer, sanitized, cdkeyMenuInfo.cdkey.field.maxchars + 1 );
		}

		cdkeyMenuInfo.cdkey.field.cursor = strlen( cdkeyMenuInfo.cdkey.field.buffer );
		cdkeyMenuInfo.cdkey.field.scroll = 0;
		UI_PopMenu();
		break;

	case ID_BACK:
		UI_PopMenu();
		break;

	case ID_TYPE:
		cdkeyMenuInfo.credentialKind = cdkeyMenuInfo.type.curvalue;
		cdkeyMenuInfo.cdkey.field.buffer[0] = '\0';
		cdkeyMenuInfo.cdkey.field.cursor = 0;
		cdkeyMenuInfo.cdkey.field.scroll = 0;
		break;

	default:
		break;
	}
}
/*
=================
UI_CDKeyMenu_PreValidateKey
=================
*/
static int UI_CDKeyMenu_PreValidateKey( const char *key ) {
	const char *cursor;
	int length;
	int ch;

	if ( cdkeyMenuInfo.autoProvisioned ) {
		return 0;
	}

	if ( cdkeyMenuInfo.credentialKind != UI_CREDENTIAL_KIND_LEGACY ) {
		return ( key && key[0] ) ? 0 : 1;
	}

	if ( !key || !key[0] ) {
		return 1;
	}

	length = strlen( key );
	if ( length != 16 ) {
		return 1;
	}

	cursor = key;
	while ( ( ch = *cursor++ ) != 0 ) {
		switch ( tolower( (unsigned char)ch ) ) {
		case '2':
		case '3':
		case '7':
		case 'a':
		case 'b':
		case 'c':
		case 'd':
		case 'g':
		case 'h':
		case 'j':
		case 'l':
		case 'p':
		case 'r':
		case 's':
		case 't':
		case 'w':
			continue;
		default:
			return -1;
		}
	}

	return 0;
}
/*
=================
UI_CDKeyMenu_DrawKey
=================
*/
static void UI_CDKeyMenu_DrawKey( void *self ) {
	menufield_s *f;
	qboolean focus;
	int style;
	float *color;
	int x, y;
	int validation;
	char sanitized[MAX_EDIT_LINE];
	const char *status;
	const char *instructions;
	int fieldWidth;

	f = (menufield_s *)self;

	if ( cdkeyMenuInfo.autoProvisioned ) {
		const char *autoMessage = uiCredentialAutoMessages[cdkeyMenuInfo.credentialKind];
		if ( !autoMessage || !autoMessage[0] ) {
			autoMessage = "Credentials are managed automatically by your platform.";
		}
		UI_DrawProportionalString( 320, 240, autoMessage, UI_CENTER|UI_SMALLFONT, color_white );
		UI_DrawProportionalString( 320, 272, "Launch through the linked platform to refresh the credential.", UI_CENTER|UI_SMALLFONT, color_white );
		return;
	}

	focus = ( f->generic.parent->cursor == f->generic.menuPosition );
	style = UI_LEFT | UI_SMALLFONT;
	color = focus ? color_yellow : color_orange;

	if ( focus ) {
		style |= UI_PULSE;
	}

	fieldWidth = f->field.widthInChars * SMALLCHAR_WIDTH;
	x = 320 - fieldWidth / 2;
	y = f->generic.y;

	UI_FillRect( x - 4, y - 4, fieldWidth + 8, SMALLCHAR_HEIGHT + 8, listbar_color );
	MField_Draw( &f->field, x, y, style, color );

	instructions = uiCredentialKindPrompts[cdkeyMenuInfo.credentialKind];
	UI_DrawProportionalString( 320, y - 36, instructions, UI_CENTER|UI_SMALLFONT, color_white );

	UI_CDKeyMenu_StripWhitespace( sanitized, sizeof( sanitized ), f->field.buffer );
	validation = UI_CDKeyMenu_PreValidateKey( sanitized );
	if ( validation == 0 ) {
		status = uiCredentialKindSuccess[cdkeyMenuInfo.credentialKind];
		color = color_white;
	} else if ( validation > 0 ) {
		status = uiCredentialKindPrompts[cdkeyMenuInfo.credentialKind];
		color = color_yellow;
	} else {
		status = uiCredentialKindErrors[cdkeyMenuInfo.credentialKind];
		color = color_red;
	}

	UI_DrawProportionalString( 320, y + 32, status, UI_CENTER|UI_SMALLFONT, color );
}
/*
===============
UI_CDKeyMenu_Init
===============
*/
static void UI_CDKeyMenu_Init( void ) {
	char stored[MAX_EDIT_LINE];

	trap_Cvar_Set( "ui_cdkeychecked", "1" );

	UI_CDKeyMenu_Cache();

	memset( &cdkeyMenuInfo, 0, sizeof( cdkeyMenuInfo ) );
	cdkeyMenuInfo.menu.wrapAround = qtrue;
	cdkeyMenuInfo.menu.fullscreen = qtrue;

	cdkeyMenuInfo.banner.generic.type = MTYPE_BTEXT;
	cdkeyMenuInfo.banner.generic.x = 320;
	cdkeyMenuInfo.banner.generic.y = 16;
	cdkeyMenuInfo.banner.string = "ACCOUNT CREDENTIAL";
	cdkeyMenuInfo.banner.color = color_white;
	cdkeyMenuInfo.banner.style = UI_CENTER;

	cdkeyMenuInfo.frame.generic.type = MTYPE_BITMAP;
	cdkeyMenuInfo.frame.generic.name = ART_FRAME;
	cdkeyMenuInfo.frame.generic.flags = QMF_INACTIVE;
	cdkeyMenuInfo.frame.generic.x = 142;
	cdkeyMenuInfo.frame.generic.y = 118;
	cdkeyMenuInfo.frame.width = 359;
	cdkeyMenuInfo.frame.height = 256;

	cdkeyMenuInfo.type.generic.type = MTYPE_SPINCONTROL;
	cdkeyMenuInfo.type.generic.name = "Credential Type";
	cdkeyMenuInfo.type.generic.flags = QMF_PULSEIFFOCUS | QMF_SMALLFONT;
	cdkeyMenuInfo.type.generic.x = 320;
	cdkeyMenuInfo.type.generic.y = 196;
	cdkeyMenuInfo.type.generic.id = ID_TYPE;
	cdkeyMenuInfo.type.generic.callback = UI_CDKeyMenu_Event;
	cdkeyMenuInfo.type.itemnames = uiCredentialKindNames;
	cdkeyMenuInfo.type.numitems = UI_CREDENTIAL_KIND_COUNT;
	cdkeyMenuInfo.type.curvalue = UI_CREDENTIAL_KIND_LEGACY;

	cdkeyMenuInfo.cdkey.generic.type = MTYPE_FIELD;
	cdkeyMenuInfo.cdkey.generic.flags = QMF_SMALLFONT | QMF_PULSEIFFOCUS;
	cdkeyMenuInfo.cdkey.generic.x = 320;
	cdkeyMenuInfo.cdkey.generic.y = 252;
	cdkeyMenuInfo.cdkey.field.widthInChars = 40;
	cdkeyMenuInfo.cdkey.field.maxchars = MAX_CREDENTIAL_CHARS - 1;
	cdkeyMenuInfo.cdkey.generic.ownerdraw = UI_CDKeyMenu_DrawKey;

	cdkeyMenuInfo.accept.generic.type = MTYPE_BITMAP;
	cdkeyMenuInfo.accept.generic.name = ART_ACCEPT0;
	cdkeyMenuInfo.accept.generic.flags = QMF_RIGHT_JUSTIFY | QMF_PULSEIFFOCUS;
	cdkeyMenuInfo.accept.generic.id = ID_ACCEPT;
	cdkeyMenuInfo.accept.generic.callback = UI_CDKeyMenu_Event;
	cdkeyMenuInfo.accept.generic.x = 640;
	cdkeyMenuInfo.accept.generic.y = 480 - 64;
	cdkeyMenuInfo.accept.width = 128;
	cdkeyMenuInfo.accept.height = 64;
	cdkeyMenuInfo.accept.focuspic = ART_ACCEPT1;

	cdkeyMenuInfo.back.generic.type = MTYPE_BITMAP;
	cdkeyMenuInfo.back.generic.name = ART_BACK0;
	cdkeyMenuInfo.back.generic.flags = QMF_LEFT_JUSTIFY | QMF_PULSEIFFOCUS;
	cdkeyMenuInfo.back.generic.id = ID_BACK;
	cdkeyMenuInfo.back.generic.callback = UI_CDKeyMenu_Event;
	cdkeyMenuInfo.back.generic.x = 0;
	cdkeyMenuInfo.back.generic.y = 480 - 64;
	cdkeyMenuInfo.back.width = 128;
	cdkeyMenuInfo.back.height = 64;
	cdkeyMenuInfo.back.focuspic = ART_BACK1;

	Menu_AddItem( &cdkeyMenuInfo.menu, &cdkeyMenuInfo.banner );
	Menu_AddItem( &cdkeyMenuInfo.menu, &cdkeyMenuInfo.frame );
	Menu_AddItem( &cdkeyMenuInfo.menu, &cdkeyMenuInfo.type );
	Menu_AddItem( &cdkeyMenuInfo.menu, &cdkeyMenuInfo.cdkey );
	Menu_AddItem( &cdkeyMenuInfo.menu, &cdkeyMenuInfo.accept );
	if ( uis.menusp ) {
		Menu_AddItem( &cdkeyMenuInfo.menu, &cdkeyMenuInfo.back );
	}

	trap_GetCDKey( stored, sizeof( stored ) );
	cdkeyMenuInfo.credentialKind = UI_CDKeyMenu_ParseCredentialKind( stored );
	cdkeyMenuInfo.type.curvalue = cdkeyMenuInfo.credentialKind;
	cdkeyMenuInfo.autoProvisioned = qfalse;

	if ( cdkeyMenuInfo.credentialKind == UI_CREDENTIAL_KIND_LEGACY && stored[0] ) {
		if ( trap_VerifyCDKey( stored, NULL ) == qfalse ) {
			stored[0] = '\\0';
		}
	}

	if ( stored[0] ) {
		if ( cdkeyMenuInfo.credentialKind == UI_CREDENTIAL_KIND_LEGACY ) {
			UI_CDKeyMenu_CopyCredentialToField( stored, cdkeyMenuInfo.credentialKind );
		} else {
			cdkeyMenuInfo.autoProvisioned = qtrue;
			cdkeyMenuInfo.cdkey.field.buffer[0] = '\\0';
		}
	} else {
		cdkeyMenuInfo.credentialKind = UI_CREDENTIAL_KIND_LEGACY;
		cdkeyMenuInfo.type.curvalue = UI_CREDENTIAL_KIND_LEGACY;
		cdkeyMenuInfo.cdkey.field.buffer[0] = '\\0';
	}

	UI_CDKeyMenu_UpdateVisibility();
}
/*
=================
UI_CDKeyMenu_Cache
=================
*/
void UI_CDKeyMenu_Cache( void ) {
	trap_R_RegisterShaderNoMip( ART_ACCEPT0 );
	trap_R_RegisterShaderNoMip( ART_ACCEPT1 );
	trap_R_RegisterShaderNoMip( ART_BACK0 );
	trap_R_RegisterShaderNoMip( ART_BACK1 );
	trap_R_RegisterShaderNoMip( ART_FRAME );
}


/*
===============
UI_CDKeyMenu
===============
*/
void UI_CDKeyMenu( void ) {
	UI_CDKeyMenu_Init();
	UI_PushMenu( &cdkeyMenuInfo.menu );
}


/*
===============
UI_CDKeyMenu_f
===============
*/
void UI_CDKeyMenu_f( void ) {
	UI_CDKeyMenu();
}
