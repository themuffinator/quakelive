#ifndef QLR_CLIENT_MATH_H
#define QLR_CLIENT_MATH_H

#include <stddef.h>
#include <stdint.h>

/*
 * Lightweight math helpers used by the annotated client runtime shims.
 * The original engine mixes vec3_t[3] arrays with pointer arithmetic; the
 * typedefs below record the explicit field widths that the reverse engineered
 * stubs expect.  They are intentionally POD friendly so that offsetof() based
 * layout tables in client_offsets.h remain valid.
 */
typedef struct {
    float x;
    float y;
    float z;
} qlr_vec3f_t; /* sizeof == 12 bytes */

typedef struct {
    float r;
    float g;
    float b;
    float a;
} qlr_color4f_t; /* sizeof == 16 bytes */

/*
 * The frame loop frequently lerps between historic server times when
 * integrating new snapshots.  A dedicated helper keeps the annotated sources
 * free from accidental dependency on the original Q3 vector macros.
 */
static inline float qlr_lerp_scalar(float from, float to, float frac) {
    return from + (to - from) * frac;
}

static inline void qlr_lerp_vec3(const qlr_vec3f_t *from,
                                 const qlr_vec3f_t *to,
                                 float frac,
                                 qlr_vec3f_t *out) {
    out->x = qlr_lerp_scalar(from->x, to->x, frac);
    out->y = qlr_lerp_scalar(from->y, to->y, frac);
    out->z = qlr_lerp_scalar(from->z, to->z, frac);
}

#endif /* QLR_CLIENT_MATH_H */
