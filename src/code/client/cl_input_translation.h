/*
=============
CL Input Translation Helpers
=============
*/
#ifndef CL_INPUT_TRANSLATION_H
#define CL_INPUT_TRANSLATION_H

#include "q_shared.h"

typedef struct {
	int key;
	int dispatchKey;
	int charCode;
	qboolean hasChar;
} clTranslatedKey_t;

clTranslatedKey_t CL_TranslateRetailKeycode( int key );
int CL_TranslateRetailMouseDelta( int delta, float cpiValue );

#endif
