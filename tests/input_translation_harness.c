#include "cl_input_translation.h"

#if defined(_WIN32)
#define QLR_TEST_EXPORT __declspec(dllexport)
#else
#define QLR_TEST_EXPORT
#endif

/*
=============
QLR_TranslateKey

Wrapper used by the Python harness to exercise CL_TranslateRetailKeycode.
=============
*/
QLR_TEST_EXPORT clTranslatedKey_t QLR_TranslateKey( int key ) {
	return CL_TranslateRetailKeycode( key );
}

/*
=============
QLR_EncodeUtf8Codepoint

Wrapper used by the Python harness to exercise CL_EncodeUtf8Codepoint.
=============
*/
QLR_TEST_EXPORT int QLR_EncodeUtf8Codepoint( int codepoint, char *buffer, int bufferSize ) {
	return CL_EncodeUtf8Codepoint( codepoint, buffer, bufferSize );
}

/*
=============
QLR_TranslateMouse

Wrapper used by the Python harness to exercise CL_TranslateRetailMouseDelta.
=============
*/
QLR_TEST_EXPORT int QLR_TranslateMouse( int delta, float cpi ) {
	return CL_TranslateRetailMouseDelta( delta, cpi );
}
