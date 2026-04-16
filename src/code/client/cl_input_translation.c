/*
=============
CL Input Translation Helpers

Retail-native translations used to normalise key codes, UTF-8
characters, and mouse deltas before dispatching into UI or
client game consumers.
=============
*/
#include <ctype.h>
#include <math.h>

#include "cl_input_translation.h"

/*
=============
CL_TranslateRetailKeycode

Translate a raw engine key code into the dispatch value expected
by the UI and client game, while also exposing the printable
character payload (UTF-8 aware) when available.
=============
*/
clTranslatedKey_t CL_TranslateRetailKeycode( int key ) {
	clTranslatedKey_t translated;

	translated.key = key;
	translated.dispatchKey = key;
	translated.charCode = 0;
	translated.hasChar = qfalse;

	if ( key < 0 ) {
		translated.key = 0;
		translated.dispatchKey = 0;
		return translated;
	}

	if ( key >= 'A' && key <= 'Z' ) {
		translated.dispatchKey = tolower( key );
	}

	if ( key > 0 && key <= 0x10FFFF ) {
		translated.charCode = key;
		translated.hasChar = qtrue;
	}

	return translated;
}

/*
=============
CL_EncodeUtf8Codepoint

Encode a single Unicode codepoint into the same UTF-8 byte
sequence that retail Quake Live's WM_CHAR path feeds into the
field and UI handlers after WideCharToMultiByte.
=============
*/
int CL_EncodeUtf8Codepoint( int codepoint, char *buffer, int bufferSize ) {
	if ( !buffer || bufferSize <= 0 ) {
		return 0;
	}

	if ( codepoint < 0 || codepoint > 0x10FFFF ) {
		return 0;
	}

	if ( codepoint >= 0xD800 && codepoint <= 0xDFFF ) {
		return 0;
	}

	if ( codepoint <= 0x7F ) {
		if ( bufferSize < 1 ) {
			return 0;
		}

		buffer[0] = (char)codepoint;
		return 1;
	}

	if ( codepoint <= 0x7FF ) {
		if ( bufferSize < 2 ) {
			return 0;
		}

		buffer[0] = (char)( 0xC0 | ( codepoint >> 6 ) );
		buffer[1] = (char)( 0x80 | ( codepoint & 0x3F ) );
		return 2;
	}

	if ( codepoint <= 0xFFFF ) {
		if ( bufferSize < 3 ) {
			return 0;
		}

		buffer[0] = (char)( 0xE0 | ( codepoint >> 12 ) );
		buffer[1] = (char)( 0x80 | ( ( codepoint >> 6 ) & 0x3F ) );
		buffer[2] = (char)( 0x80 | ( codepoint & 0x3F ) );
		return 3;
	}

	if ( bufferSize < 4 ) {
		return 0;
	}

	buffer[0] = (char)( 0xF0 | ( codepoint >> 18 ) );
	buffer[1] = (char)( 0x80 | ( ( codepoint >> 12 ) & 0x3F ) );
	buffer[2] = (char)( 0x80 | ( ( codepoint >> 6 ) & 0x3F ) );
	buffer[3] = (char)( 0x80 | ( codepoint & 0x3F ) );
	return 4;
}

/*
=============
CL_TranslateRetailMouseDelta

Scale a single mouse delta using the retail CPI-derived conversion
so UI and client game consumers observe the same deltas that the
native Win32 pipeline exposes after TranslateMessage/DispatchMessage
runs.
=============
*/
int CL_TranslateRetailMouseDelta( int delta, float cpiValue ) {
	float scale;

	if ( cpiValue > 0.0f ) {
		scale = 1000.0f / cpiValue;
		delta = (int)lrintf( (float)delta * scale );
	}

	return delta;
}
