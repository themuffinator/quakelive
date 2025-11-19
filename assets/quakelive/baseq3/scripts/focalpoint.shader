//**********************************************************************//
//
//	focalpoint.shader for QL by Sims
// "Focal Point"
//	Website : http://www.simonoc.com/
//
//**********************************************************************//
//
// ======================================================================
// Used inside skybox portal only on model
//
textures/focal/skyportal
{
	qer_editorimage textures/focal/sky_edit.jpg

	q3map_noFog
	q3map_globalTexture
	surfaceparm sky
	surfaceparm noimpact
	surfaceparm nolightmap
	skyparms textures/focal/env/sky 1500 -
	nopicmip

	{
		map textures/focal/cloud_edge.tga
		blendfunc GL_ONE_MINUS_SRC_ALPHA GL_SRC_ALPHA
		tcMod scale 2 2
		tcMod transform 0.125 0 0 0.125 0.1075 0.1075
		rgbGen identityLighting
	}
	{
		map textures/focal/env/sky_mask.tga
		blendfunc GL_ONE_MINUS_SRC_ALPHA GL_SRC_ALPHA
		tcMod transform 0.25 0 0 0.25 0.1075 0.1075
		rgbGen identityLighting
	}
}

// ======================================================================
// Used to link together the sky surface in the map and the portal sky
//
textures/focal/sky
{
	qer_editorimage textures/focal/sky_edit.jpg

	//red green blue intensity degrees elevation deviance samples
//	q3map_sunExt 1 1 .93 150 270 50 2 32
	q3map_sunExt 1 1 .95 400 -30 45 2 32
	q3map_skyLight 100 6

	q3map_noFog
	q3map_globalTexture
	surfaceparm sky
	surfaceparm noimpact
	surfaceparm nolightmap
	nopicmip
	skyparms - - -
}

// ----------------------------------------------------------------------
textures/focal/skyportal_cloudupper
{
	qer_editorimage textures/focal/cloud_upper.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		clampMap textures/focal/cloud_upper.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		rgbGen wave sin 0.8 0.1 0 0.25
		tcmod rotate 5
	}
}

// ----------------------------------------------------------------------
textures/focal/skyportal_swirl4upper
{
	qer_editorimage textures/focal/cloud_swirl4.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		clampMap textures/focal/cloud_swirl4.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		rgbGen wave sin 0.7 0.1 0.75 0.25
		tcMod stretch sin 0.95 0.05 0 0.1
		tcmod rotate 15
	}
}

// ----------------------------------------------------------------------
textures/focal/skyportal_cloudedge
{
	qer_editorimage textures/focal/cloud_edge.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		clampMap textures/focal/cloud_edge.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		rgbGen wave sin 0.6 0.05 0 0.25
		tcMod stretch sin 0.95 0.05 0 0.01
		tcmod rotate 5
	}
}

// ----------------------------------------------------------------------
textures/focal/skyportal_beaminner
{
	qer_editorimage textures/focal/marker_dust.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none

   {
		// Upward pulse effect in portal skybox
		map textures/focal/portal_pulse.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		rgbGen wave sin 0.5 0.2 0 0.1
		tcMod scale 1 -5
		tcMod scroll 0.25 1
	}
	{
		map textures/focal/stars_bright.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcmod scale 0.75 3
		tcMod Scroll 0.01 -0.3
	}
	{
		map textures/focal/stars_motionbright.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		rgbGen const ( 0.5 0.5 1 )
		tcmod scale 0.75 3
		tcMod Scroll -0.025 -0.4
		detail
	}
}

// ----------------------------------------------------------------------
textures/focal/skyportal_groundbeam1
{
	qer_editorimage textures/focal/marker_dust.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	qer_trans 0.9
	cull none
	
   {
		// Solid glow at base of ground beam
		map textures/focal/marker_dust.tga
		blendfunc add
		rgbGen wave sin 0.7 0.3 0.5 0.1
		tcMod scale 1 0.5
		tcMod scroll 0.25 0
	}
	{
		map textures/focal/stars.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcmod scale 1 0.5
		tcMod Scroll 0.2 -0.5
	}
	{
		map textures/focal/stars.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcmod scale 2 0.35
		tcMod Scroll -0.2 -0.4
		detail
	}
}


// ----------------------------------------------------------------------
textures/focal/skyportal_groundbeam2
{
	qer_editorimage textures/focal/marker_dust.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none

//	deformVertexes wave 192 sin 0 4 0.2 0.2
   {
		// Pre-pulse buildup
		map textures/focal/marker_dust.tga
		blendfunc add
		rgbGen wave sin 0.7 0.3 0.9 1
		tcMod scale 1 0.75
		tcMod scroll 0.25 0
	}
	{
		map textures/focal/stars.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcmod scale 1 0.5
		tcMod Scroll -0.2 -0.15
	}
	{
		map textures/focal/stars_motion.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		rgbgen wave square 0.8 0.2 0.5 4
		tcMod scale 1 0.5
		tcMod scroll -0.1 -0.65
		detail
	}	
}
// ----------------------------------------------------------------------
textures/focal/skyportal_groundbeam3
{
	qer_editorimage textures/focal/marker_dust.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	qer_trans 0.9
	cull none
	
   {
	// Upward pulse effect on ground beam
		map textures/focal/portal_pulse.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		rgbGen wave sin 0.7 0.2 0 0.1
		tcMod scale 1 -1
		tcMod scroll 0.25 1
	}
	{
		map textures/focal/stars_motion.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcmod scale 1 0.5
		tcMod Scroll -0.05 -0.2
	}
	{
		map textures/focal/stars_motion.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		rgbGen const ( 0.5 0.5 1 )
		tcmod scale 0.5 1
		tcMod Scroll -0.025 -0.4
		detail
	}
}

// ======================================================================
// Lights
// ======================================================================
textures/focal/light1_10k
{
	qer_editorimage textures/focal/light1_yellow.tga
	q3map_lightImage textures/focal/light1_yellow_colour.tga
	q3map_surfacelight 4000
	q3map_nonplanar
	q3map_shadeangle 60
	q3map_forceMeta
	surfaceparm trans
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_light1_yellow.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/focal/x_light1_yellow_blend.tga
		blendfunc add
		rgbGen wave sin .8 .2 0 0.25
	}
}

// ======================================================================
// Vertical panels
// ======================================================================
textures/focal/v016
{
	qer_editorimage textures/focal/v016.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_v016.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/v032
{
	qer_editorimage textures/focal/v032.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_v032.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/v048
{
	qer_editorimage textures/focal/v048.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_v048.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/v064
{
	qer_editorimage textures/focal/v064.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_v064.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/v128
{
	qer_editorimage textures/focal/v128.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_v128.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/v256
{
	qer_editorimage textures/focal/v256.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_v256.tga
		blendfunc filter
	}
}

// ======================================================================
// DARK Vertical panels
// ======================================================================
textures/focal/v032dark
{
	qer_editorimage textures/focal/v032dark.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_v032dark.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/v064dark
{
	qer_editorimage textures/focal/v064dark.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_v064dark.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/v128dark
{
	qer_editorimage textures/focal/v128dark.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_v128dark.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/v256dark
{
	qer_editorimage textures/focal/v256dark.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_v256dark.tga
		blendfunc filter
	}
}

// ======================================================================
// Step panels
// ======================================================================
textures/focal/step16
{
	qer_editorimage textures/focal/step16.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_step16.tga
		blendfunc filter
	}
}
// ======================================================================
// Square floor panels
// ======================================================================
textures/focal/sqr16
{
	qer_editorimage textures/focal/sqr16.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_sqr16.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/sqr24
{
	qer_editorimage textures/focal/sqr24.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_sqr24.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/sqr32
{
	qer_editorimage textures/focal/sqr32.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_sqr32.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/sqr64
{
	qer_editorimage textures/focal/sqr64.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_sqr64.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/sqrgrate
{
	qer_editorimage textures/focal/sqrgrate.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_sqrgrate.tga
		blendfunc filter
	}
}
// ----------------------------------------------------------------------
textures/focal/sqrgrate32
{
	qer_editorimage textures/focal/sqrgrate32.tga
	q3map_nonplanar
	q3map_shadeangle 45
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/focal/x_sqrgrate32.tga
		blendfunc filter
	}
}

// ======================================================================
// Floor decal markers and jumppads
// ======================================================================
textures/focal/marker_cog
{
	qer_editorimage textures/focal/marker_cog.tga
	surfaceparm nolightmap
   surfaceparm nonsolid
	surfaceparm trans
   surfaceparm nomarks
   polygonOffset

	{
		clampMap textures/focal/x_marker_cogcenter.tga
		blendfunc blend
		rgbGen vertex
		rgbGen wave sin 0.9 0.1 0.5 0.1
		tcMod stretch sin 0.7 0.2 0 0.1
		tcMod rotate -45
	}
   {
		clampMap textures/focal/x_marker_cog.tga
      blendfunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen vertex
   }
   {
		clampMap textures/focal/x_marker_cog.tga
		blendfunc blend
		rgbGen vertex
	}
	{
		clampMap textures/focal/x_marker_cog.tga
		blendfunc blend
		rgbGen vertex
		rgbGen wave sin 0.85 0 0 0
		tcMod stretch sin 0.8 0 0 0
		tcMod rotate -30
	}
}
// ----------------------------------------------------------------------
textures/focal/marker_dust
{
	qer_editorimage textures/focal/marker_dust.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	polygonOffset
	nomipmaps
	cull none
	sort 6

   {
		map textures/focal/marker_dust.tga
		blendfunc add
		rgbGen wave sin 0.7 0.3 0.5 0.1
		tcMod scroll 0.25 0
		detail
	}
}
// ----------------------------------------------------------------------
textures/focal/weapon_cog
{
	qer_editorimage textures/focal/weapon_cog.tga
	surfaceparm nolightmap
   surfaceparm nonsolid
	surfaceparm trans
   surfaceparm nomarks
   polygonOffset

	{
		clampMap textures/focal/x_marker_cogcenter.tga
		blendfunc blend
		rgbGen vertex
		rgbGen const ( 0.7 0.8 0.5 )
		tcMod stretch sin 0.7 0.2 0.5 0.15
		tcMod rotate -45
	}
   {
		clampMap textures/focal/x_marker_cog.tga
      blendfunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen vertex
   }
   {
		clampMap textures/focal/x_marker_cog.tga
		blendfunc blend
		rgbGen vertex
	}
	{
		clampMap textures/focal/x_marker_cog.tga
		blendfunc blend
		rgbGen vertex
		rgbGen const ( 0.6 0.8 0.4 )
		tcMod stretch sin 0.8 0 0 0
		tcMod rotate -30
	}
}
// ----------------------------------------------------------------------
textures/focal/weapon_dust
{
	qer_editorimage textures/focal/weapon_dust.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	polygonOffset
	nomipmaps
	cull none
	sort 6

   {
		map textures/focal/weapon_dust.tga
		blendfunc add
		rgbGen wave sin 0.7 0.3 0.5 0.1
		tcMod scroll 0.25 0
		detail
	}
}

// ----------------------------------------------------------------------
textures/focal/focal_cog
{
	qer_editorimage textures/focal/weapon_cog.tga
	surfaceparm nolightmap
   surfaceparm nonsolid
	surfaceparm trans
   surfaceparm nomarks
   polygonOffset

   {
		clampMap textures/focal/x_marker_focalswirl.tga
		blendfunc blend
		rgbGen vertex
		rgbGen wave sin 0.8 0.2 0 0.1
		tcMod stretch sin 0.85 0 0 0
		tcmod rotate 135
	}
	{
		clampMap textures/focal/x_marker_focalcog.tga
		blendfunc blend
		rgbGen vertex
	}
}

// ----------------------------------------------------------------------
textures/focal/jumppad_blue
{    
	qer_editorimage textures/focal/jumppad_blue.tga
	q3map_lightImage textures/focal/jumppad_blue_colour.tga
	q3map_surfacelight 1000
	q3map_nonplanar
	q3map_shadeangle 60
	nomipmaps
   
	{
		clampMap textures/focal/x_jumppad_blue.tga
		rgbGen wave sin 1 0.2 0.5 0.1
		tcMod stretch sin 0.6 0.2 0 0.5
		tcMod rotate -180
		rgbGen identity
	}
	{
		clampMap textures/focal/x_jumppad_blue.tga
		blendfunc blend
		rgbGen identity
	}
	{
		clampMap textures/focal/x_jumppad_edge.tga
		blendfunc blend
		tcMod rotate -135
		rgbGen identity
	}
	{
		Map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

// ----------------------------------------------------------------------
textures/focal/jumppad_blue_grate
{    
	qer_editorimage textures/focal/jumppad_blue_grate.tga
	q3map_lightImage textures/focal/jumppad_blue_colour.tga
	q3map_surfacelight 1000
	q3map_nonplanar
	q3map_shadeangle 60
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		clampMap textures/focal/x_jumppad_blue_grate.tga
		blendfunc filter
	}
}

// ----------------------------------------------------------------------
textures/focal/jumppad_blue_nofx
{    
	qer_editorimage textures/focal/jumppad_blue_nofx.tga
	q3map_lightImage textures/focal/jumppad_blue_colour.tga
	q3map_surfacelight 1000
	q3map_nonplanar
	q3map_shadeangle 60
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		clampMap textures/focal/x_jumppad_blue.tga
		blendfunc filter
	}
}

// ----------------------------------------------------------------------
textures/focal/jumppad_dust
{
	qer_editorimage textures/focal/marker_dust.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	qer_trans 0.9
	cull none
   {
		map textures/focal/marker_dust.tga
		blendfunc add
		rgbGen wave sin 0.7 0.3 0.5 0.1
		tcMod scroll 0.25 0
	}
	{
		map textures/focal/stars.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcmod scale 2 0.5
		tcMod Scroll 0.2 -0.15
	}
	{
		map textures/focal/stars.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcmod scale 3 0.15
		tcMod Scroll -0.2 -0.15
		detail
	}
}

// ----------------------------------------------------------------------
textures/focal/jumppad_dust_outer
{
	qer_editorimage textures/focal/marker_dust.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	qer_trans 0.9
	cull none
	
	{
		map textures/focal/stars_motion.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcmod scale 2 0.25
		tcMod Scroll -0.05 -0.2
	}
	{
		map textures/focal/stars.tga
		blendfunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcmod scale 3 0.15
		tcMod Scroll -0.2 -0.15
		detail
	}
}

// ----------------------------------------------------------------------
textures/focal/decal_spawn
{
	qer_editorimage textures/focal/x_marker_cog.tga
   surfaceparm nonsolid
	surfaceparm trans
   surfaceparm nomarks
	surfaceparm nolightmap
   polygonOffset
   {
		clampMap textures/focal/x_marker_cog.tga
      blendfunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen vertex
   }
   {
		clampMap textures/focal/x_marker_cog.tga
		blendfunc blend
		rgbGen vertex
	}
}

// ----------------------------------------------------------------------
// Defines map lightgrid area
textures/focal/lightgrid
{
	qer_editorimage textures/common/lightgrid.tga
	qer_trans 0.5
	surfaceparm nodraw
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm detail
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm lightgrid
}

// ----------------------------------------------------------------------
// solid black, no lightmap, used for shadows
textures/focal/black_nodraw
{
	qer_editorimage textures/focal/black_nodraw.tga
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm noimpact
	{
		map textures/focal/black_nodraw.tga
		blendfunc add
		rgbGen const ( 0 0 0 )
	}
}

// ======================================================================
// Sponsors for competition
// ----------------------------------------------------------------------
textures/focal/sponsors
{
	qer_editorimage textures/focal/sponsors.tga
   surfaceparm nonsolid
	surfaceparm trans
   surfaceparm nomarks
	surfaceparm nolightmap
   polygonOffset
   {
      map textures/focal/sponsors.tga
      blendfunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
   }
}

// ======================================================================
// alpha fade shaders
// (c) 2004 randy reddig
// http://www.shaderlab.com
// ======================================================================
// Only needed for compiling
//
textures/focal/alpha_000	// Primary texture ONLY
{
	qer_editorimage textures/focal/alpha_000.tga
	q3map_alphaMod volume
	q3map_alphaMod set 0
	surfaceparm nodraw
	surfaceparm nonsolid
	surfaceparm trans
	qer_trans 0.7
}
textures/focal/alpha_025	// Primary texture ONLY
{
	qer_editorimage textures/focal/alpha_025.tga
	q3map_alphaMod volume
	q3map_alphaMod set 0.25
	surfaceparm nodraw
	surfaceparm nonsolid
	surfaceparm trans
	qer_trans 0.7
}
textures/focal/alpha_050	// Primary texture ONLY
{
	qer_editorimage textures/focal/alpha_050.tga
	q3map_alphaMod volume
	q3map_alphaMod set 0.50
	surfaceparm nodraw
	surfaceparm nonsolid
	surfaceparm trans
	qer_trans 0.7
}
textures/focal/alpha_100	// Secondary texture ONLY
{
	qer_editorimage textures/focal/alpha_100.tga
	q3map_alphaMod volume
	q3map_alphaMod set 1.0
	surfaceparm nodraw
	surfaceparm nonsolid
	surfaceparm trans
	qer_trans 0.7
}
