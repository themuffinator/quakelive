#include "cl_input_translation.h"

/*
=============
QLR_TranslateKey

Wrapper used by the Python harness to exercise CL_TranslateRetailKeycode.
=============
*/
clTranslatedKey_t QLR_TranslateKey( int key ) {
	return CL_TranslateRetailKeycode( key );
}

/*
=============
QLR_TranslateMouse

Wrapper used by the Python harness to exercise CL_TranslateRetailMouseDelta.
=============
*/
int QLR_TranslateMouse( int delta, float cpi ) {
	return CL_TranslateRetailMouseDelta( delta, cpi );
}
