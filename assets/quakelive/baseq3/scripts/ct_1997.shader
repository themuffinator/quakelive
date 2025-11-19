//LIGHT 2:1

textures/ct_1997/geolight_01
{
	qer_editorimage textures/ct_1997/geolight_01.tga
	surfaceparm nomarks
	q3map_surfacelight 2000
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/geolight_01.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/ct_1997/geolight_01_blend.tga
		blendfunc add
	}
}

//BANNER

textures/ct_1997/banner_01
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/banner_01.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/banner_01_still
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
	 qer_editorimage textures/ct_1997/banner_01.tga
	{
        map textures/ct_1997/banner_01.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/banner_02
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/banner_02.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/1_tall
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/1_tall.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/1_tall_r
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/1_tall_r.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/2_tall_r
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/2_tall_r.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/3_short
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/3_short.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/3_tall
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/3_tall.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/3_tall_r
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/3_tall_r.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/4_short
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/4_short.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/4_tall
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/4_tall.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/ct_1997/4_tall_r
{
     cull disable
     surfaceparm alphashadow
     surfaceparm trans	
     surfaceparm nomarks
	 surfaceparm nonsolid
     tessSize 64
     deformVertexes wave 30 sin 0 2 0 .2
     deformVertexes wave 100 sin 0 2 0 .7
	{
        map textures/ct_1997/4_tall_r.tga
        alphaFunc GE128
		depthWrite
		rgbGen identity
    }
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

//ROCK

textures/ct_1997/rock_02
{
	qer_editorimage textures/ct_1997/rock_02.tga
	
	q3map_nonplanar
	q3map_shadeAngle 90
	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/rock_02.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/ct_1997/rock_02b
{
	qer_editorimage textures/ct_1997/rock_02b.tga
	
	q3map_nonplanar
	q3map_shadeAngle 90
	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/rock_02b.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

//LIGHTS

textures/ct_1997/baslt_01
{
	qer_editorimage textures/ct_1997/baslt_01.tga
	surfaceparm nomarks
	q3map_surfacelight 2000
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/baslt_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_1997/baslt_01_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_1997/baslt_02
{
	qer_editorimage textures/ct_1997/baslt_02.tga
	surfaceparm nomarks
	q3map_surfacelight 2000
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/baslt_02.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_1997/baslt_02_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_1997/geolight4_01_2k
{
	qer_editorimage textures/ct_1997/geolight4_01.tga
	surfaceparm nomarks
	q3map_surfacelight 2000
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/geolight4_01.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/shw/geolight4_01.blend.tga
		blendfunc add
	}
}

//RG WATER PIT FOG

textures/ct_1997/waterfog
{
	qer_editorimage textures/sfx/fog_grey.tga
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm 	nolightmap
	q3map_globaltexture
		fogparms ( .210 .200 .150 ) 768
	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc gl_dst_color gl_zero
		tcmod scale -.05 -.05
		tcmod scroll .01 -.01
		rgbgen identity
	}
	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc gl_dst_color gl_zero
		tcmod scale .05 .05
		tcmod scroll .01 -.01
		rgbgen identity
	}
}

textures/ct_1997/hellfog
{
	qer_editorimage textures/sfx/fog_grey.tga
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm 	nodrop
	surfaceparm 	nolightmap
	q3map_globaltexture
	q3map_surfacelight 100
	fogparms ( .40 .06 .01 ) 512
	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc gl_dst_color gl_zero
		tcmod scale -.05 -.05
		tcmod scroll .01 -.01
		rgbgen identity
	}
	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc gl_dst_color gl_zero
		tcmod scale .05 .05
		tcmod scroll .01 -.01
		rgbgen identity
	}
}

//TELEPORTER FLARES

textures/ct_1997/tp_flare_01
{
	qer_editorimage textures/ct_1997/tp_flare_01.jpg
	qer_trans .5	
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformVertexes autosprite
	deformvertexes move 0 0 80 sawtooth 0 1 1 1
	{
		clampmap textures/ct_1997/tp_flare_01.jpg
		rgbGen wave sawtooth 1 -1 1 1
		blendfunc add
	}
}

textures/ct_1997/tp_flare_02
{
	qer_editorimage textures/ct_1997/tp_flare_01.jpg
	qer_trans .5		
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformVertexes autosprite
	deformvertexes move 0 0 80 sawtooth 0 1 .75 1
	{
		clampmap textures/ct_1997/tp_flare_01.jpg
		rgbGen wave sawtooth 1 -1 .75 1
		blendfunc add
	}
}

textures/ct_1997/tp_flare_03
{
	qer_editorimage textures/ct_1997/tp_flare_01.jpg
	qer_trans .5		
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformVertexes autosprite
	deformvertexes move 0 0 80 sawtooth 0 1 .5 1
	{
		clampmap textures/ct_1997/tp_flare_01.jpg
		rgbGen wave sawtooth 1 -1 .5 1
		blendfunc add
	}
}

textures/ct_1997/tp_flare_04
{
	qer_editorimage textures/ct_1997/tp_flare_01.jpg
	qer_trans .5		
	surfaceparm noimpact
	surfaceparm nolightmap
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nodlight
	deformVertexes autosprite
	deformvertexes move 0 0 80 sawtooth 0 1 .25 1
	{
		clampmap textures/ct_1997/tp_flare_01.jpg
		rgbGen wave sawtooth 1 -1 .25 1
		blendfunc add
	}
}

//TP PLATE

textures/ct_1997/tp_plate_01
{
	q3map_lightimage textures/ct_1997/tp_plate_01.tga
	qer_editorimage textures/ct_1997/tp_plate_01.tga
	surfaceparm nomarks
	polygonOffset
	sort 6
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/tp_plate_01.tga
		blendFunc filter
		rgbGen identity
	}
        {
		map textures/ct_1997/tp_plate_01_blend.tga
		blendFunc add
		rgbGen wave sawtooth .5 .5 0 1
	}
	
}

textures/ct_1997/tp_plate_01_decal
{
	q3map_lightimage textures/ct_1997/tp_plate_01.tga
	qer_editorimage textures/ct_1997/tp_plate_01.tga
	surfaceparm nomarks
	polygonOffset 
	sort 6 
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/tp_plate_01.tga
		blendFunc filter
		rgbGen identity
	}
        {
		map textures/ct_1997/tp_plate_01_blend.tga
		blendFunc add
		rgbGen wave sawtooth .5 .5 0 1
	}
	
}

//FLARES

textures/ct_1997/flare_olive
{
	qer_editorimage textures/ct_1997/flare_olive.tga
	surfaceparm trans
	surfaceparm nomarks
    surfaceparm nonsolid
	surfaceparm nolightmap
	qer_trans 0.5
	cull none
	deformVertexes autosprite
	//nopicmip
	{
		map textures/ct_1997/flare_olive.tga
		blendfunc gl_one gl_one_minus_src_color
		rgbGen identity
	}
}

textures/ct_1997/flare_red
{
	qer_editorimage textures/ct_1997/flare_red.tga
	surfaceparm trans
	surfaceparm nomarks
    	surfaceparm nonsolid
	surfaceparm nolightmap
	qer_trans 0.5
	cull none
	deformVertexes autosprite
	//nopicmip
	{
		map textures/ct_1997/flare_red.tga
		blendfunc gl_one gl_one_minus_src_color
		rgbGen identity
	}
}

textures/ct_1997/flare_yellow
{
	qer_editorimage textures/ct_1997/flare_yellow.tga
	surfaceparm trans
	surfaceparm nomarks
    surfaceparm nonsolid
	surfaceparm nolightmap
	qer_trans 0.5
	cull none
	deformVertexes autosprite
	//nopicmip
	{
		map textures/ct_1997/flare_yellow.tga
		blendfunc gl_one gl_one_minus_src_color
		rgbGen identity
	}
}

textures/ct_1997/beam_1_blue
{
	qer_editorimage textures/ct_1997/beam_1_blue.tga
    surfaceparm trans	
    surfaceparm nomarks	
    surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nomipmaps
    nopicmip
	{
		map textures/ct_1997/beam_1_blue.tga
        tcMod Scroll .3 0
        blendFunc add
        }
}

textures/ct_1997/beam_1_yellow
{
	qer_editorimage textures/ct_1997/beam_1_yellow.tga
    surfaceparm trans	
    surfaceparm nomarks	
    surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nomipmaps
    nopicmip
	{
		map textures/ct_1997/beam_1_yellow.tga
        tcMod Scroll .3 0
        blendFunc add
        }
}

//GLASS
textures/ct_1997/glass
{
	qer_editorimage textures/ct_1997/glass.tga
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm nodlight
	surfaceparm trans
	qer_trans 0.5
	cull disable
	sort 7
    {
        map textures/ct_1997/glass.tga
        blendfunc filter
    }
}

//LIGHT BEAM

textures/ct_1997/lightbeam_01_3k
{
	surfaceparm nomarks
	q3map_surfacelight 3000
	q3map_lightsubdivide 32
	q3map_lightimage textures/ct_1997/lb_beam_01_blend.tga
	qer_editorimage textures/ct_1997/lb_beam_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/lb_beam_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_1997/lb_beam_01_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/ct_1997/lightbeam_01_1k
{
	surfaceparm nomarks
	q3map_surfacelight 1000
	q3map_lightsubdivide 32
	q3map_lightimage textures/ct_1997/lb_beam_01_blend.tga
	qer_editorimage textures/ct_1997/lb_beam_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/lb_beam_01.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/ct_1997/lb_beam_01_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

//LIQUIDS

textures/ct_1997/stroyent
{
	qer_editorimage textures/ct_1997/fluid_orange_bubble1.tga
	q3map_lightimage textures/ct_1997/fluid_orange_bubble1.tga
	q3map_globaltexture
	qer_trans .75
	surfaceparm noimpact
	surfaceparm slime
	surfaceparm nolightmap
	surfaceparm trans
	tessSize 32
	cull disable
	//deformVertexes wave 100 sin 0 1 .5 .5
	{
		map textures/ct_1997/fluid_orange_bubble2.tga
		blendfunc add
		tcMod turb .3 .2 1 .05
		tcMod scroll .01 .01
	}	
	{
		map textures/ct_1997/fluid_orange_bubble5.tga
		blendfunc add
		tcMod turb .2 .1 1 .05
		tcMod scroll .01 .01
	}
	{
		map textures/ct_1997/fluid03_orange.tga
		blendfunc add
		tcMod turb .2 .1 .1 .2
		tcMod scroll .001 .001
	}		
}

//NONSOLID ROPE/CABLE/CRATE

textures/ct_1997/concrete_01d_nonsolid
{
	qer_editorimage textures/ct_1997/concrete_01d.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/concrete_01d.tga
		blendfunc filter
	}
}

textures/ct_1997/crate_01_nonsolid
{
	qer_editorimage textures/ct_1997/crate_01.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/crate_01.tga
		blendfunc filter
	}
}

textures/ct_1997/crate_top_01_nonsolid
{
	qer_editorimage textures/ct_1997/crate_top_01.tga
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ct_1997/crate_top_01.tga
		blendfunc filter
	}
}


//SKY

textures/ct_1997/EDGESKY
{
	qer_editorimage textures/skies/inteldimredclouds.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	surfaceparm sky
	skyparms - 256 -
	
	//q3map_sunExt 0.957809 0.710403 0.546902 150 220 65 3 16 //1 0.932311 0.77821 150 220 50 3 16
	q3map_sunExt 0.97 0.75 0.45 200 220 65 3 16 
	q3map_lightmapFilterRadius 0 12		//self other
	q3map_skyLight 150 3 //100 3
	{
		map textures/skies/inteldimclouds.tga
		tcMod scale 3 2
		tcMod scroll 0.15 0.15
		depthWrite
	}
	{
		map textures/skies/intelredclouds.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 3 3
		tcMod scroll 0.05 0.05
	}
}

//MUD STAIN

textures/ct_1997/decal_stain_01
{
	nopicmip
	polygonOffset
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		map textures/ct_1997/decal_stain_01.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
	}
}

//FENCE NONSOLID

textures/ct_1997/fence_shadow_nonsolid
{
	qer_editorimage textures/phantq3dm3/fence_shadow.tga
	surfaceparm trans
	surfaceparm alphashadow		
	surfaceparm nonsolid
	cull none
    nopicmip
	{
		map textures/phantq3dm3/fence_shadow.tga
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

//TERRAIN

textures/ct_1997/grass
{
	qer_editorimage textures/ct_1997/grass.tga
	{
		map textures/ct_1997/grass.tga
		rgbGen identity
	}
}

//textures/ct_1997/grass_nomip
//{
//	qer_editorimage textures/ct_1997/grass_nomip.tga
//	nopicmip
//	novlcollapse
//	{
//		map textures/ct_1997/grass_nomip.tga
//		rgbGen identity
//	}
//}

textures/ct_1997/grass_rock
{
	qer_editorimage textures/ct_1997/grass_rock.tga
	{
		map textures/ct_1997/grass.tga	// Primary (dp2 Vertical)
		tcmod scale 2 2
		rgbGen identity
	}
	{
		map textures/ct_1997/rock_02b.tga	// Secondary (dp2 Horizontal)
		tcmod scale 2 2
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/ct_1997/grass_rock_nomip
{
	qer_editorimage textures/ct_1997/sand_rock.tga
	//qer_editorimage textures/terrain/qzterra1_rock1_grass1_ed.tga
	nopicmip
	novlcollapse
	{
		map textures/ct_1997/grass.tga	// Primary (dp2 Vertical)
		tcmod scale 2 2
		rgbGen identity
	}
	{
		map textures/ct_1997/rock_02b.tga	// Secondary (dp2 Horizontal)
		tcmod scale 2 2
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/ct_1997/sand_grass
{
	qer_editorimage textures/ct_1997/sand_grass.tga
	{
		map textures/ct_1997/sand.tga	// Primary (dp2 Vertical)
		rgbGen identity
	}
	{
		map textures/ct_1997/grass.tga	// Secondary (dp2 Horizontal)
		tcmod scale 2 2
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/ct_1997/sand_rock
{
	qer_editorimage textures/ct_1997/sand_rock.tga
	{
		map textures/ct_1997/sand.tga	// Primary (dp2 Vertical)
		rgbGen identity
	}
	{
		map textures/ct_1997/rock_02b.tga	// Secondary (dp2 Horizontal)
		tcmod scale 2 2
		blendfunc blend
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/ct_1997/rock_02b
{
	qer_editorimage textures/ct_1997/rock_02b.tga
	{
		map textures/ct_1997/rock_02b.tga
		rgbGen identity
	}
}

//textures/ct_1997/rock_02b_nomip
//{
//	qer_editorimage textures/ct_1997/rock_02b.tga
//	nopicmip
//	novlcollapse
//	{
//		map textures/ct_1997/rock_02b.tga
//		rgbGen identity
//	}
//}

//SUPPORT BEAM

textures/ct_1997/support_beam_01
{
	qer_editorimage textures/ct_1997/support_beam_01.tga
	surfaceparm	metalsteps	
	surfaceparm trans	
	surfaceparm alphashadow
    surfaceparm nomarks	
	cull none
        nopicmip
	{
		map textures/ct_1997/support_beam_01.tga
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

//STEAM
textures/ct_1997/steam
{
	qer_editorimage textures/ct_1997/steam_01.tga
	nopicmip
	cull none
	nomipmaps
    {
		map textures/ct_1997/steam_01.tga
        blendfunc add
        rgbGen wave Inversesawtooth -0.25 1 0 1
        tcmod scroll 1 0
	}
    {
		map textures/ct_1997/steam_01.tga
        blendfunc add
        rgbGen wave Inversesawtooth -0.25 1 0 2
        tcmod scroll 2 0
	}
    {
		map textures/ct_1997/steam_02.tga
        blendfunc add
        rgbGen wave Inversesawtooth -0.25 1 0.25 3
        tcmod scroll 3 0
	}
    {
		map textures/ct_1997/steam_02.tga
        blendfunc add
        rgbGen wave Inversesawtooth -0.25 1 0.25 4
        tcmod scroll 4 0
	}
}

//CONVEYOR
textures/ct_1997/stroy_conveyor
{
	qer_editorimage textures/ct_1997/stroy_conveyor_ed.tga
    surfaceparm nomarks	
	{
		map textures/ct_1997/stroy_conveyor.tga
		tcmod scroll 0 1.5625
	}
	{
		map $lightmap
		blendfunc filter
		rgbgen identity
	}
}

//SCREENS
textures/ct_1997/screen_01
{
	qer_editorimage textures/ct_1997/screen_01.tga
	qer_trans 0.40
	surfaceparm nonsolid
	surfaceparm nomarks
	nopicmip
	cull disable	
	{
		map textures/ct_1997/screen_01.tga
		rgbGen wave triangle 0.44 0.12 0 0.8
		blendfunc add
	}
	{
		map textures/ct_1997/screen_01.tga
		rgbGen wave triangle 0.05 0.05 1 2.2
		blendfunc add
	}
	{
		map textures/ad_content/adbrightoverlay.tga
		rgbGen Wave sin .12 0.05 0 2
		tcmod scroll 1 0.2
		blendfunc add
	}
}

textures/ct_1997/screen_02
{
	qer_editorimage textures/ct_1997/screen_02.tga
	qer_trans 0.40
	surfaceparm nonsolid
	surfaceparm nomarks
	nopicmip
	cull disable	
	{
		map textures/ct_1997/screen_02.tga
		rgbGen wave triangle 0.75 0.15 0 0.8
		blendfunc add
	}
	{
		map textures/ct_1997/screen_02.gui.tga
		rgbGen wave triangle 0.8 0.1 1 1.25
		blendfunc add
	}
	{
		clampmap textures/ct_1997/screen_02.overlay.tga
		rgbGen Wave sin .12 0.05 0 2.5
		alphaFunc GE128
		blendfunc add
	}
}

//JUMPPAD WALL

textures/ct_1997/wall_jump
{
	qer_editorimage textures/ct_1997/wall_jump.tga
	{
		map textures/sfx2/rlaunch3.tga
		rgbGen identity
		tcmod scale 1 .5
		tcmod scroll 0 1.42
	}
	{
		map textures/ct_1997/wall_jump.tga
		blendFunc blend
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc GL_DST_COLOR GL_ZERO
	}	
}