#ifndef BG_PMOVE_JUMP_H
#define BG_PMOVE_JUMP_H

/*
=============
PM_EvaluateJumpVelocityScale

Calculates the jump velocity scaling multiplier based on the latest
qualifying ground contact and returns the observed time delta.
=============
*/
static inline float PM_EvaluateJumpVelocityScale( const playerState_t *ps, const pmove_settings_t *settings, int commandTime, int *outTimeDelta ) {
	int		entryCount;
	int		index;
	int		i;
	int		lastContactTime;
	int		timeDelta;
	float		threshold;
	float		offset;
	float		scaleAdd;

	if ( outTimeDelta ) {
		*outTimeDelta = -1;
	}

	if ( !ps || !settings ) {
		return 1.0f;
	}

	entryCount = ps->groundTraceHistoryCount;
	if ( entryCount <= 0 ) {
		entryCount = 0;
	}
	if ( entryCount > PS_GROUND_TRACE_HISTORY ) {
		entryCount = PS_GROUND_TRACE_HISTORY;
	}

	lastContactTime = 0;

	if ( entryCount > 0 ) {
		index = ps->groundTraceHistoryIndex;
		if ( index < 0 || index >= PS_GROUND_TRACE_HISTORY ) {
			if ( PS_GROUND_TRACE_HISTORY > 0 ) {
				index %= PS_GROUND_TRACE_HISTORY;
				if ( index < 0 ) {
					index += PS_GROUND_TRACE_HISTORY;
				}
			} else {
				index = 0;
			}
		}

		for ( i = 0; i < entryCount; i++ ) {
			int		entNum;
			int		contactTime;

			if ( index < 0 || index >= PS_GROUND_TRACE_HISTORY ) {
				break;
			}

			entNum = ps->groundTraceEntNums[index];
			contactTime = ps->groundTraceTimes[index];

			if ( entNum != ENTITYNUM_NONE && contactTime > 0 && contactTime <= commandTime ) {
				if ( ps->groundTraceNormals[index][2] >= MIN_WALK_NORMAL ) {
					lastContactTime = contactTime;
					break;
				}
			}

			if ( entryCount <= 1 ) {
				break;
			}

			index--;
			if ( index < 0 ) {
				index = PS_GROUND_TRACE_HISTORY - 1;
			}
		}
	}

	timeDelta = -1;
	if ( lastContactTime > 0 ) {
		timeDelta = commandTime - lastContactTime;
		if ( timeDelta < 0 ) {
			timeDelta = 0;
		}
	}

	if ( outTimeDelta ) {
		*outTimeDelta = timeDelta;
	}

	if ( timeDelta < 0 ) {
		return 1.0f;
	}

	threshold = settings->jumpVelocityTimeThreshold;
	offset = settings->jumpVelocityTimeThresholdOffset;
	scaleAdd = settings->jumpVelocityScaleAdd;

	if ( offset != 0.0f ) {
		threshold += offset;
	}

	if ( threshold <= 0.0f ) {
		return 1.0f;
	}

	if ( scaleAdd <= 0.0f ) {
		return 1.0f;
	}

	if ( (float)timeDelta > threshold ) {
		return 1.0f;
	}

	return 1.0f + scaleAdd;
}

#endif // BG_PMOVE_JUMP_H
