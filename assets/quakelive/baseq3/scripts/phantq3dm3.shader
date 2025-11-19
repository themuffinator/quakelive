//-----------------------------------------------------------------
//-----Tom 'Phantazm11' Perryman
//-----www.phantazm11.com
//-----phantazm11(at)gmail[dot]com
//-----08.01.2010
//-----------------------------------------------------------------

textures/phantq3dm3/tp_base_rust_01_nonsolid
{
	qer_editorimage textures/phantq3dm3/tp_base_rust_01.tga
	surfaceparm	nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_base_rust_01.tga
		blendfunc filter
	}
}

textures/phantq3dm3/tp_base_rust_02_nonsolid
{
	qer_editorimage textures/phantq3dm3/tp_base_rust_02.tga
	surfaceparm	nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_base_rust_02.tga
		blendfunc filter
	}
}

textures/phantq3dm3/tp_metal_floor_001_nonsolid
{
	qer_editorimage textures/phantq3dm3/tp_metal_floor_001.tga
	surfaceparm	nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_metal_floor_001.tga
		blendfunc filter
	}
}

textures/phantq3dm3/tp_sign_machine
{
	qer_editorimage textures/phantq3dm3/tp_sign_machine.tga
    surfaceparm trans	
	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset	
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_sign_machine.tga
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

textures/phantq3dm3/tp_sign_slip
{
	qer_editorimage textures/phantq3dm3/tp_sign_slip.tga
    surfaceparm trans	
	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset	
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_sign_slip.tga
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

textures/phantq3dm3/tp_machine_light
{
	qer_editorimage textures/phantq3dm3/tp_machine_light.tga
    surfaceparm trans	
    surfaceparm nomarks
	q3map_surfacelight 150
	cull none
    nopicmip
	polygonoffset
	{
		map textures/phantq3dm3/tp_machine_light.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{	map textures/phantq3dm3/tp_machine_light_add.tga
		blendFunc add
	}
}
textures/phantq3dm3/tp_lightbeam_001
{
    surfaceparm trans	
    surfaceparm nomarks	
    surfaceparm nonsolid
	surfaceparm nolightmap
	nopicmip
	cull none
	
	{
		map textures/phantq3dm3/tp_lightbeam_001.tga
        blendFunc add
    }
}

textures/phantq3dm3/jp_sfx
{
	qer_editorimage textures/phantq3dm3/jp_sfx.tga
	surfaceparm nolightmap
	surfaceparm	trans
	surfaceparm nonsolid
	surfaceparm nomarks
	qer_trans 0.9
	cull none
	{
		map textures/phantq3dm3/jp_sfx.tga
		blendFunc GL_SRC_ALPHA GL_ONE
		rgbGen vertex
		tcmod scale 2 0.15
		tcMod Scroll 0.2 0.06
		detail
	}
}
textures/phantq3dm3/tp_base_light_10k
{
	qer_editorimage textures/phantq3dm3/tp_base_light_001.tga
	surfaceparm nomarks
	q3map_surfacelight 10000
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_base_light_001.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_base_light_001_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}


textures/phantq3dm3/tp_base_light_002
{
	qer_editorimage textures/phantq3dm3/tp_base_light_002.tga
	surfaceparm nomarks
	q3map_surfacelight 5000
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_base_light_002.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_base_light_002_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/phantq3dm3/tp_fog
{
	qer_editorimage textures/phantq3dm3/tp_fog.tga
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm fog
	fogparms ( 0.5647058 0.5294117 0.3333333 ) 5000
}

textures/phantq3dm3/tp_clouds_001

{
	skyparms - 512 -
	q3map_lightImage textures/phantq3dm3/tp_clouds_001.tga
	q3map_sunExt .77 .91 1 175 -75 55 3 16
	q3map_lightmapFilterRadius 0 8		//self other
	q3map_skyLight 100 3
	surfaceparm sky
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nodlight
	nopicmip
	qer_editorimage textures/phantq3dm3/tp_clouds_001.tga
	{
		map textures/phantq3dm3/tp_clouds_001.tga
		tcMod scale 2 2
		depthWrite
	}
} 

textures/phantq3dm3/tp_fan_rusted
{
	qer_editorimage textures/phantq3dm3/tp_fan_rusted.tga
    surfaceparm trans	
    surfaceparm nomarks	
	cull none
    nopicmip
	{
		clampmap textures/phantq3dm3/tp_fan_rusted.tga
		tcMod rotate 450
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

textures/phantq3dm3/tp_fan_rusted_150
{
	qer_editorimage textures/phantq3dm3/tp_fan_rusted.tga
    surfaceparm trans	
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		clampmap textures/phantq3dm3/tp_fan_rusted.tga
		tcMod rotate 150
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

textures/phantq3dm3/tp_fan_shadow
{
	qer_editorimage textures/phantq3dm3/tp_fan_shadow.tga
    surfaceparm nolightmap
    surfaceparm trans	
    surfaceparm nomarks	
	cull none
	polygonoffset
    nopicmip
	{
		clampmap textures/phantq3dm3/tp_fan_shadow.tga
		tcMod rotate 350 
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
		rgbGen exactVertex
        depthWrite
	}
}

textures/phantq3dm3/fence_shadow
{
	qer_editorimage textures/phantq3dm3/fence_shadow.tga
	surfaceparm trans
	surfaceparm alphashadow	
    surfaceparm nomarks		
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

textures/phantq3dm3/tp_wires_001
{
	cull disable
	surfaceparm alphashadow
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	nopicmip
	{
		map textures/phantq3dm3/tp_wires_001.tga
		alphaFunc GE128
		depthWrite
		rgbGen vertex
	}
    {
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}

textures/phantq3dm3/jp_bumper_light
{
	qer_editorimage textures/base_light/ceil1_39.tga
	surfaceparm nomarks
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_39.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_39.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/phantq3dm3/jp_bumper_light_nonsolid
{
	qer_editorimage textures/base_light/ceil1_39.tga
	surfaceparm nomarks
	surfaceparm nonsolid
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_39.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_39.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/phantq3dm3/tp_stain_001
{
	nopicmip
	polygonOffset
	surfaceparm nomarks
	{
		map textures/phantq3dm3/tp_stain_001.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
	}
}

textures/phantq3dm3/tp_stain_002
{
	nopicmip
	polygonOffset
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		map textures/phantq3dm3/tp_stain_002.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
	}
}

textures/phantq3dm3/tp_stain_003
{
	nopicmip
	polygonOffset
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		map textures/phantq3dm3/tp_stain_003.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
	}
}

textures/phantq3dm3/tp_stain_004
{
	nopicmip
	polygonOffset
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		map textures/phantq3dm3/tp_stain_004.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
	}
}

textures/phantq3dm3/tp_stain_005
{
	nopicmip
	polygonOffset
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		map textures/phantq3dm3/tp_stain_005.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
	}
}

textures/phantq3dm3/tp_stain_006
{
	nopicmip
	polygonOffset
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		map textures/phantq3dm3/tp_stain_006.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
	}
}

textures/phantq3dm3/tp_stain_007
{
	nopicmip
	polygonOffset
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		map textures/phantq3dm3/tp_stain_007.tga
		blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
	}
}

textures/phantq3dm3/tp_factorywindow_001
{
	q3map_surfacelight 10
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_factorywindow_001.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_factorywindow_001_blend.tga
		blendFunc GL_ONE GL_ONE
	}
}

textures/phantq3dm3/tp_factorywindow_002
{
	q3map_surfacelight 10
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_factorywindow_002.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_factorywindow_002_blend.tga
		blendFunc GL_ONE GL_ONE
	}
}

textures/phantq3dm3/tp_factorywindow_003
{
	q3map_surfacelight 10
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_factorywindow_003.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_factorywindow_003_blend.tga
		blendFunc GL_ONE GL_ONE
	}
}

textures/phantq3dm3/tp_skylight_001
{
	q3map_surfacelight 85
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_skylight_001.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_skylight_001_add.tga
		blendFunc GL_ONE GL_ONE
	}
}

textures/phantq3dm3/tp_skylight_002
{
	q3map_surfacelight 85
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_skylight_002.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_skylight_002_add.tga
		blendFunc GL_ONE GL_ONE
	}
}

textures/phantq3dm3/tp_factorywindow_001_1
{
	qer_editorimage textures/phantq3dm3/tp_factorywindow_001.tga
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
  	{
		map textures/phantq3dm3/tp_factorywindow_001.tga
     	blendFunc GL_DST_COLOR GL_ZERO
     	rgbGen identity
   	}
}

textures/phantq3dm3/tp_rust_trim_002
{	
	cull none    	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_rust_trim_002.tga
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantq3dm3/tp_rust_trim_002_nonsolid
{	
	qer_editorimage textures/phantq3dm3/tp_rust_trim_002.tga
	cull none    	
	surfaceparm nonsolid
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_rust_trim_002.tga
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantq3dm3/tp_rust_trim_003
{
	surfaceparm metalsteps
	surfaceparm alphashadow		
	cull none
	{
		map textures/phantq3dm3/tp_rust_trim_003.tga
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

textures/phantq3dm3/tp_rust_trim_003_solid
{
	qer_editorimage textures/phantq3dm3/tp_rust_trim_003.tga
	surfaceparm metalsteps	
	cull none	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_rust_trim_003.tga
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantq3dm3/tp_slime
{              
	qer_editorimage textures/phantq3dm3/tp_slime.tga
	q3map_globaltexture
	qer_trans .80
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm water
	cull disable
	nopicmip
	{
		map textures/phantq3dm3/tp_slime_1.tga
		blendfunc GL_ONE GL_ONE //SRC_COLOR
		tcMod scroll .02 .02
                       
	}
	{
		map textures/liquids/proto_poolpass.tga
		blendfunc GL_ONE GL_ONE
		tcMod scale .5 .6
		tcMod scroll .06 .04
	}
	{
		map textures/phantq3dm3/tp_slime.tga
		blendfunc GL_ONE GL_ONE
		tcMod scroll .05 .05
	}
	{
		map $lightmap
		rgbgen identity
		blendfunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantq3dm3/slime_drip
{
	qer_editorimage textures/phantq3dm3/slime_drip.tga
	surfaceparm trans   
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	nopicmip 
	sort additive  
	cull none
	deformVertexes bulge 128 1 .5
	nopicmip
	{
		map textures/phantq3dm3/slime_drip.tga
		blendFunc add //GL_ONE GL_ONE
		rgbGen vertex
		tcMod scale 1 .25
		tcMod Scroll 0 -.2
	}
}

textures/phantq3dm3/tp_pipecap
{	
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_pipecap.tga
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

textures/phantq3dm3/tp_rustedvent_001
{	
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_rustedvent_001.tga
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantq3dm3/tp_rustedvent_002
{	
	qer_editorimage textures/phantq3dm3/tp_rustedvent_001.tga
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/phantq3dm3/tp_rustedvent_001.tga
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/phantq3dm3/tp_crete_decal_1
{
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_crete_decal_1.tga
		blendFunc GL_ONE GL_SRC_ALPHA
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

textures/phantq3dm3/tp_crete_decal_2
{
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_crete_decal_2.tga
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

textures/phantq3dm3/tp_crete_decal_3
{
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_crete_decal_3.tga
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

textures/phantq3dm3/tp_crete_decal_4
{
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_crete_decal_4.tga
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

textures/phantq3dm3/tp_crete_decal_5
{
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_crete_decal_5.tga
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

textures/phantq3dm3/tp_crete_decal_6
{
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_crete_decal_6.tga
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


textures/phantq3dm3/tp_crete_decal_8
{
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_crete_decal_8.tga
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

textures/phantq3dm3/tp_crete_decal_10
{
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_crete_decal_10.tga
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

textures/phantq3dm3/tp_crete_decal_11
{
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_crete_decal_11.tga
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

textures/phantq3dm3/tp_crete_decal_12
{
	surfaceparm trans	
   	surfaceparm nonsolid
    surfaceparm nomarks
	polygonoffset
	sort 6
	nopicmip
	{
		map textures/phantq3dm3/tp_crete_decal_12.tga
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