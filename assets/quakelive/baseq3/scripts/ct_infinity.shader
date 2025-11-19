//FOG

    textures/ct_infinity/blackfog
      {
              qer_editorimage textures/ct_infinity/black.tga
              surfaceparm fog
              surfaceparm nonsolid
              surfaceparm trans
              surfaceparm nolightmap
			  qer_trans 0.5
              qer_nocarve
              fogparms ( 0 0 0 ) 1024
      }
	  
    textures/ct_infinity/greyfog
      {
              qer_editorimage textures/ct_infinity/black.tga
              surfaceparm fog
              surfaceparm nonsolid
              surfaceparm trans
              surfaceparm nolightmap
			  qer_trans 0.5
              qer_nocarve
              fogparms ( .9 .9 .9 ) 50000
      }

//FENCE

textures/ct_infinity/fence
{
	qer_editorimage textures/base_trim/proto_fence.tga
	surfaceparm trans		
	cull none
	surfaceparm nomarks
	//surfaceparm	nonsolid
    nopicmip
	surfaceparm alphashadow
	
	{
		map textures/base_trim/proto_fence.tga
		tcMod scale 3 3
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

//LIGHTS 

textures/ct_infinity/baslt4_inf_1k
{
	qer_editorimage textures/base_light/baslt4_1.tga
	surfaceparm nomarks
	q3map_surfacelight 1000

	// New Fluorescent light
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/baslt4_1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/baslt4_1.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_infinity/baslt4_inf_2k
{
	qer_editorimage textures/base_light/baslt4_1.tga
	surfaceparm nomarks
	q3map_surfacelight 2000

	// New Fluorescent light
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/baslt4_1.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/baslt4_1.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_infinity/lightbeam_01_1k
{
	surfaceparm nomarks
	q3map_surfacelight 1000
	q3map_lightsubdivide 32
	q3map_lightimage textures/ct_infinity/lb_beam_01_blend.tga
	qer_editorimage textures/ct_infinity/lb_beam_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/lb_beam_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_infinity/lb_beam_01_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_infinity/lightbeam_02_1k
{
	surfaceparm nomarks
	q3map_surfacelight 1000
	q3map_lightsubdivide 32
	q3map_lightimage textures/ct_infinity/lb_beam_02_blend.tga
	qer_editorimage textures/ct_infinity/lb_beam_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/lb_beam_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_infinity/lb_beam_02_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_infinity/lightbeam_01_3k
{
	surfaceparm nomarks
	q3map_surfacelight 3000
	q3map_lightsubdivide 32
	q3map_lightimage textures/ct_infinity/lb_beam_01_blend.tga
	qer_editorimage textures/ct_infinity/lb_beam_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/lb_beam_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_infinity/lb_beam_01_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_infinity/lightbeam_02_3k
{
	surfaceparm nomarks
	q3map_surfacelight 3000
	q3map_lightsubdivide 32
	q3map_lightimage textures/ct_infinity/lb_beam_02_blend.tga
	qer_editorimage textures/ct_infinity/lb_beam_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/lb_beam_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_infinity/lb_beam_02_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_infinity/lightbeam_03_3k
{
	surfaceparm nomarks
	q3map_surfacelight 3000
	q3map_lightsubdivide 32
	q3map_lightimage textures/ct_infinity/lb_beam_03_blend.tga
	qer_editorimage textures/ct_infinity/lb_beam_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/lb_beam_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_infinity/lb_beam_03_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}


textures/ct_infinity/lamp_white_10k
{
	surfaceparm nomarks
	q3map_surfacelight 10000
	q3map_lightimage textures/ct_infinity/lamp_white_blend.tga
	qer_editorimage textures/ct_infinity/lamp_white.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/lamp_white.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_infinity/lamp_white_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_infinity/lamp_white2_8k
{
	surfaceparm nomarks
	q3map_surfacelight 9000
	q3map_lightimage textures/ct_infinity/lamp_white2_blend.tga
	qer_editorimage textures/ct_infinity/lamp_white2.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/lamp_white2.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_infinity/lamp_white2_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_infinity/lamp_white2_1k
{
	surfaceparm nomarks
	q3map_surfacelight 1000
	q3map_lightimage textures/ct_infinity/lamp_white2_blend.tga
	qer_editorimage textures/ct_infinity/lamp_white2.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/lamp_white2.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_infinity/lamp_white2_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_infinity/lamp_white2_4k
{
	surfaceparm nomarks
	q3map_surfacelight 4000
	q3map_lightimage textures/ct_infinity/lamp_white2_blend.tga
	qer_editorimage textures/ct_infinity/lamp_white2.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/lamp_white2.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_infinity/lamp_white2_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_infinity/lamp_03_4k
{
	surfaceparm nomarks
	q3map_surfacelight 4000
	q3map_lightimage textures/ct_infinity/lamp_03_blend.tga
	qer_editorimage textures/ct_infinity/lamp_03.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/lamp_03.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_infinity/lamp_03_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

//GRATES

textures/ct_infinity/grate_02_trans
{
	surfaceparm	metalsteps	
        surfaceparm trans		
	surfaceparm nonsolid  //Tim's fuckage
	qer_editorimage textures/ct_infinity/grate_02.tga
	cull none
    nopicmip
	surfaceparm alphashadow

	// A GRATE OR GRILL THAT CAN BE SEEN FROM BOTH SIDES
	{
		map textures/ct_infinity/grate_02.tga
		//tcMod scale 2 2
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/ct_infinity/grate_02c_trans
{
	surfaceparm	metalsteps	
        surfaceparm trans
	qer_editorimage textures/ct_infinity/grate_02c.tga		
	surfaceparm nonsolid  //Tim's fuckage
	cull none
    nopicmip
	surfaceparm alphashadow

	// A GRATE OR GRILL THAT CAN BE SEEN FROM BOTH SIDES
	{
		map textures/ct_infinity/grate_02c.tga
		//tcMod scale 2 2
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/ct_infinity/water_nofog
	{
		qer_editorimage textures/ct_infinity/tele1.tga
		qer_trans .5
		q3map_globaltexture
		surfaceparm trans
		surfaceparm nonsolid
		surfaceparm water
	
		cull disable
		deformVertexes wave 64 sin .05 .05 0 .5	
		{ 
			map textures/ct_infinity/tele1.tga
			blendFunc GL_dst_color GL_one
			rgbgen identity
			tcmod scale .5 .5
			tcmod scroll .025 .01
		}
	
		{ 
			map textures/ct_infinity/tele2.tga
			blendFunc GL_dst_color GL_one
			tcmod scale -.5 -.5
			tcmod scroll .025 .025
		}

	
		{
			map $lightmap
			blendFunc GL_dst_color GL_zero
			rgbgen identity		
		}
	}

//JUMPPAD

textures/ct_infinity/jumppad_01_red
{
	q3map_lightimage textures/ct_infinity/jumppadsmall_red.tga
	qer_editorimage textures/ct_infinity/jumppadsmall_red.tga
	surfaceparm nomarks
	q3map_surfacelight 1000
	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/jumppad_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		clampmap textures/ct_infinity/jumppadsmall_red.tga
		blendfunc add
		tcMod stretch sin 1 2 0 1.2
		//rgbGen wave square .5 .5 .25 1.2
	}
}

textures/ct_infinity/jumppad_01_blue
{
	q3map_lightimage textures/ct_infinity/jumppadsmall_blue.tga
	qer_editorimage textures/ct_infinity/jumppadsmall_blue.tga
	surfaceparm nomarks
	q3map_surfacelight 1000
	light 1
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/jumppad_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		clampmap textures/ct_infinity/jumppadsmall_blue.tga
		blendfunc add
		tcMod stretch sin 1 2 0 1.2
		//rgbGen wave square .5 .5 .25 1.2
	}
}

//TELE

textures/ct_infinity/tele_exit
{
   noPicMip
   polygonOffset
   sort 6
   surfaceparm nonsolid
   surfaceparm nomarks
   {
      map textures/ct_infinity/tele_exit.tga
      blendFunc GL_DST_COLOR GL_ONE
   }
}

textures/ct_infinity/tele
{
	qer_editorimage textures/ct_infinity/tp1.jpg
	q3map_surfacelight 100
	surfaceparm noimpact
	surfaceparm nomarks
	surfaceparm nolightmap
	nopicmip
	tesssize 128
	cull disable
	deformVertexes wave 70 sin 2 1 .1 0.1
	
	{
		map textures/gothic_trim/pitted_rust3_black.tga
		tcMod scale 2 2
	}
	{
		map textures/ct_infinity/tp1.jpg
		tcMod turb 0 .3 0 .2
		blendFunc GL_ONE GL_ZERO
	}
	{
		map textures/ct_infinity/tp2.jpg
		tcMod turb .4 .1 0 .2
		blendFunc GL_ONE GL_ZERO
	}
	
}

//gauges

textures/ct_infinity/gauge_01_360
{
	qer_editorimage textures/ct_infinity/gauge_01.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/gauge_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		clampmap textures/ct_infinity/gauge_01_blend.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		tcmod rotate 360
	}
}

textures/ct_infinity/gauge_01_540
{
	qer_editorimage textures/ct_infinity/gauge_01.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/gauge_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		clampmap textures/ct_infinity/gauge_01_blend.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		tcmod rotate 540
	}
}

textures/ct_infinity/bluelight
{
	q3map_lightimage textures/base_light/proto_lightblue.tga
	qer_editorimage textures/base_light/proto_lightblue.tga
	surfaceparm nomarks
	q3map_surfacelight 3000
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/proto_lightblue.tga
		blendFunc filter
		rgbGen identity
	}
        {
		map textures/base_light/proto_lightblue.tga
		blendFunc add
		rgbGen wave square .5 .5 0 1
	}
	
}

textures/ct_infinity/redlight
{
	q3map_lightimage textures/base_light/proto_lightred.tga
	qer_editorimage textures/base_light/proto_lightred.tga
	surfaceparm nomarks
	q3map_surfacelight 3000
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/proto_lightred.tga
		blendFunc filter
		rgbGen identity
	}
        {
		map textures/base_light/proto_lightred.tga
		blendFunc add
		rgbGen wave square .5 .5 0 1
	}
	
}

//FLARES

textures/ct_infinity/flare_white
{
	qer_editorimage textures/ct_infinity/flare_white.tga
	surfaceparm trans
	surfaceparm nomarks
    	surfaceparm nonsolid
	surfaceparm nolightmap
	qer_trans 0.5
	cull none
	deformVertexes autosprite
	nopicmip
	{
		map textures/ct_infinity/flare_white.tga
		blendfunc add
		rgbGen identity
	}
}

//WOOD FLOOR

textures/ct_infinity/wood
{
	qer_editorimage textures/ct_infinity/floor_03.tga
	surfaceparm	woodsteps
	
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/ct_infinity/floor_03.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/ct_infinity/wood_sheet
{
	qer_editorimage textures/ct_infinity/floor_04.tga
	surfaceparm	woodsteps
	
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/ct_infinity/floor_04.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

//METAL FLOORS

textures/ct_infinity/clang_floor
{
	qer_editorimage textures/ct_infinity/floor_02.tga
	surfaceparm	metalsteps
	
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/ct_infinity/floor_02.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/ct_infinity/grate_02
{
	qer_editorimage textures/ct_infinity/grate_02.tga
	surfaceparm	metalsteps
	
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/ct_infinity/grate_02.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/ct_infinity/trim_07
{
	qer_editorimage textures/ct_infinity/trim_07.tga
	surfaceparm	metalsteps
	
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/ct_infinity/trim_07.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}
textures/ql/circle_grate_trans
{
	surfaceparm	metalsteps	
    surfaceparm trans		
	surfaceparm nonsolid
	cull none
    nopicmip
	surfaceparm alphashadow
	qer_editorimage textures/ql/circle_grate.tga
	{
		map textures/ql/circle_grate.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

//TERRAIN/ROCK

textures/ct_infinity/rock_01
{
	qer_editorimage textures/ct_infinity/rock_01.tga
	
	q3map_nonplanar
	q3map_shadeAngle 90
	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/rock_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/ct_infinity/oneway
{
	qer_editorimage textures/ct_infinity/oneway.tga
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_infinity/oneway.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}