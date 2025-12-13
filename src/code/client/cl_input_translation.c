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

	if ( key >= ' ' && key <= 0x10FFFF ) {
	translated.charCode = key;
	translated.hasChar = qtrue;
	}

	return translated;
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
