#include <stdbool.h>
#include <stdint.h>

#include "client_math.h"
#include "client_offsets.h"
#include "client_types.h"

/*
 * HUD rendering helpers reverse engineered from src/code/client/cl_scrn.c.
 * The annotated versions flatten the renderer API into a tiny shim so that
 * prototype front-ends can experiment with layout logic without linking the
 * full renderer DLL.
 */

typedef int qlr_shader_t;

typedef struct {
    qlr_shader_t (*registerShader)(const char *name);
    void (*drawStretchPic)(float x, float y, float width, float height,
                           float s1, float t1, float s2, float t2,
                           qlr_shader_t shader);
    void (*setColor)(const float *rgba);
} qlr_renderer_exports_t;

typedef struct {
    float vidWidth;
    float vidHeight;
} qlr_video_metrics_t;

typedef struct {
    qlr_renderer_exports_t re;
    qlr_video_metrics_t video;
    qlr_shader_t charSetShader;
    qlr_shader_t whiteShader;
} qlr_hud_context_t;

#define QLR_SMALLCHAR_WIDTH 8
#define QLR_SMALLCHAR_HEIGHT 16

static void qlr_adjust_from_640(const qlr_hud_context_t *ctx,
                                float *x, float *y, float *w, float *h) {
    const float xscale = ctx->video.vidWidth / 640.0f;
    const float yscale = ctx->video.vidHeight / 480.0f;

    if (x) *x *= xscale;
    if (y) *y *= yscale;
    if (w) *w *= xscale;
    if (h) *h *= yscale;
}

void QLR_SCR_DrawNamedPic(const qlr_hud_context_t *ctx,
                          float x, float y, float width, float height,
                          const char *picname) {
    if (!ctx->re.registerShader || !ctx->re.drawStretchPic) {
        return;
    }
    qlr_shader_t shader = ctx->re.registerShader(picname);
    qlr_adjust_from_640(ctx, &x, &y, &width, &height);
    ctx->re.drawStretchPic(x, y, width, height, 0.0f, 0.0f, 1.0f, 1.0f, shader);
}

void QLR_SCR_FillRect(const qlr_hud_context_t *ctx,
                      float x, float y, float width, float height,
                      const float *color) {
    if (!ctx->re.drawStretchPic || !ctx->re.setColor) {
        return;
    }
    ctx->re.setColor(color);
    qlr_adjust_from_640(ctx, &x, &y, &width, &height);
    ctx->re.drawStretchPic(x, y, width, height, 0.0f, 0.0f, 0.0f, 0.0f, ctx->whiteShader);
    ctx->re.setColor(NULL);
}

static void qlr_draw_char(const qlr_hud_context_t *ctx, int x, int y, float size, int ch) {
    if (!ctx->re.drawStretchPic || ch == ' ') {
        return;
    }

    float ax = (float)x;
    float ay = (float)y;
    float aw = size;
    float ah = size;
    qlr_adjust_from_640(ctx, &ax, &ay, &aw, &ah);

    const int row = (ch >> 4) & 15;
    const int col = ch & 15;
    const float frow = row * 0.0625f;
    const float fcol = col * 0.0625f;
    const float cell = 0.0625f;

    ctx->re.drawStretchPic(ax, ay, aw, ah,
                           fcol, frow,
                           fcol + cell, frow + cell,
                           ctx->charSetShader);
}

void QLR_SCR_DrawStringExt(const qlr_hud_context_t *ctx,
                           int x, int y, float size, const char *string,
                           const float *setColor, bool forceColor) {
    if (!string || !ctx->re.setColor) {
        return;
    }

    float currentColor[4] = {1, 1, 1, 1};
    if (setColor) {
        for (int i = 0; i < 4; ++i) {
            currentColor[i] = setColor[i];
        }
    }

    const char *s = string;
    while (*s) {
        if (forceColor) {
            ctx->re.setColor(currentColor);
        } else if ((*s == '^') && (*(s + 1) >= '0') && (*(s + 1) <= '7')) {
            int colorIndex = *(s + 1) - '0';
            float intensity = (colorIndex == 0) ? 1.0f : 0.75f;
            float alt = (colorIndex & 1) ? 0.25f : 0.75f;
            currentColor[0] = (colorIndex & 1) ? intensity : alt;
            currentColor[1] = (colorIndex & 2) ? intensity : alt;
            currentColor[2] = (colorIndex & 4) ? intensity : alt;
            s += 2;
            ctx->re.setColor(currentColor);
            continue;
        } else {
            ctx->re.setColor(currentColor);
        }

        qlr_draw_char(ctx, x, y, size, *s);
        x += (int)size;
        ++s;
    }
    ctx->re.setColor(NULL);
}

void QLR_SCR_DrawSmallChar(const qlr_hud_context_t *ctx, int x, int y, int ch) {
    if (!ctx->re.drawStretchPic || ch == ' ') {
        return;
    }
    if (y < -QLR_SMALLCHAR_HEIGHT) {
        return;
    }

    const int row = (ch >> 4) & 15;
    const int col = ch & 15;
    const float frow = row * 0.0625f;
    const float fcol = col * 0.0625f;
    const float cell = 0.0625f;

    ctx->re.drawStretchPic((float)x, (float)y, (float)QLR_SMALLCHAR_WIDTH, (float)QLR_SMALLCHAR_HEIGHT,
                           fcol, frow, fcol + cell, frow + cell,
                           ctx->charSetShader);
}

/*
 * OpenGL dependency summary:
 *  - drawStretchPic ultimately maps to glDrawArrays-style quads
 *  - setColor drives glColor4f or equivalent state
 *  - registerShader reaches into the renderer DLL's asset system
 * Stub implementations for headless tools can provide no-op callbacks while
 * preserving the HUD layout behavior for testing.
 */
