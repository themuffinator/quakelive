textures/ncts_dm1/dust_beam
{
	qer_editorimage textures/proto2/dust03.tga
	qer_trans 0.99
	cull disable
	surfaceparm trans
	surfaceparm nonsolid
	sort 10
	deformVertexes wave 50 sin 0 3 0 .2
	{
		map textures/proto2/dust03.tga
        	tcmod scroll 0 -0.015
		blendfunc blend
		rgbGen wave sin 1 .05 0 .4
	}
	{
		map textures/proto2/dust02.tga
        	tcmod scroll 0.015 0.02
		blendfunc blend
		rgbGen wave sin 0.3 .04 0 .5
	}
}

textures/ncts_dm1/sky
{
	qer_editorimage textures/skies/blacksky.tga
	surfaceparm sky
	surfaceparm nodlight
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_sunEXT 1 .977 .864 100 70 75 3 5
	q3map_lightmapFilterRadius 0 8
	q3map_skylight	75 4
	skyparms textures/desctf3/env/sky 1024 -
	nopicmip
	{
		map textures/desctf3/env/clouds.tga
		tcMod scale 1.25 1.25
		tcMod scroll 0.0075 -0.0075
		blendFunc blend
		rgbgen identityLighting
	}	
}

textures/ncts_dm1/tp_slime_filter
{              
	qer_editorimage textures/phantq3dm3/tp_slime.tga
	q3map_globaltexture
	qer_trans .80
	surfaceparm lightfilter
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm water
	cull disable
	novlcollapse
	nopicmip
	q3map_lightmapFilterRadius 0 4
	q3map_bounceScale 3
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

textures/ncts_dm1/des_chain
{
	surfaceparm nonsolid
	surfaceparm nomarks
	nopicmip
	qer_trans 0.99
	cull none
	deformVertexes autosprite2
        {
		map textures/ncts_dm1/des_chain.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphafunc GE128
		depthwrite
		rgbGen identity
	}
        {
		map $lightmap
                blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
		depthfunc equal
	}	
}

textures/ncts_dm1/des_chain2
{
	qer_editorimage textures/ncts_dm1/des_chain.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	nopicmip
	qer_trans 0.99
	cull none
        {
		map textures/ncts_dm1/des_chain.tga
		blendfunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphafunc GE128
		depthwrite
		rgbGen identity
	}
        {
		map $lightmap
                blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
		depthfunc equal
	}	
}

textures/ncts_dm1/bld_rock2algae
{
	qer_editorimage textures/desctf5/ter_algae1.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map textures/ncts_dm1/des_rock2.tga
		rgbgen identity
	}
	{
		map textures/desctf5/ter_algae1.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphaFunc GT0
		rgbgen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/ncts_dm1/ter_rockmud
{
	qer_editorimage textures/desctf3/ter_rockmud.tga
	q3map_nonplanar
	q3map_shadeangle 100
	q3map_tcGen ivector ( 128 0 0 ) ( 0 128 0 )
	q3map_alphaMod dotproduct ( 0.0 0.0 0.25 )
	{
		map textures/ncts_dm1/des_rock2.tga	// Primary
		rgbGen identity
	}
	{
		map textures/desctf3/ter_mud2.tga	// Secondary
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/ncts_dm1/bld_rock2moss
{
	qer_editorimage textures/desctf3/ter_moss1.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map textures/ncts_dm1/des_rock2.tga
		rgbGen identity
	}
	{
		map textures/desctf3/ter_moss1.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphaFunc GT0
		rgbGen identity
		alphaGen vertex
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/ncts_dm1/des_rock2
{
	qer_editorimage textures/ncts_dm1/des_rock2.tga
	q3map_nonplanar
	q3map_shadeAngle 135
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ncts_dm1/des_rock2.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/ncts_dm1/des_rock2_wet
{ 
	qer_editorimage textures/ncts_dm1/des_rock2_wet.tga
	{
		map textures/phantgothic/phantgothic_env_wood.tga
		tcgen environment
		rgbgen wave sin .12 .2 0 0
	}
	{
		map textures/ncts_dm1/des_rock2_wet.tga
		blendFunc GL_ZERO GL_SRC_ALPHA
		tcmod scale .2 .2
		rgbgen identity	
	}
	{
		map textures/ncts_dm1/des_rock2_wet.tga
		blendFunc GL_ONE GL_SRC_ALPHA
		rgbgen identity	
	}
	{
		map $lightmap
       		blendfunc gl_dst_color gl_zero
		rgbgen identity 
	}
}

textures/ncts_dm1/des_stainedglass_filter
{
   qer_editorimage textures/ncts_dm1/des_stainedglass.tga
   surfaceparm lightfilter
   surfaceparm nolightmap
   cull disable
   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
   {
      map textures/ncts_dm1/des_stainedglass.tga
      blendFunc GL_DST_COLOR GL_ZERO
      rgbGen identity
   }
}

textures/ncts_dm1/des_stainedglass
{
	qer_editorimage textures/ncts_dm1/des_stainedglass.tga
	q3map_lightimage textures/ncts_dm1/des_stainedglass.tga
	q3map_surfacelight 200
	q3map_bounceScale 64
	{
		map textures/ncts_dm1/des_stainedglass.tga
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/ncts_dm1/tp_stainedglass_001_filter
{
   qer_editorimage textures/tp_gothic/tp_stainedglass_001
   surfaceparm lightfilter
   surfaceparm nolightmap
   cull disable
   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
   {
      map textures/tp_gothic/tp_stainedglass_001.tga
      blendFunc GL_DST_COLOR GL_ZERO
      rgbGen identity
   }
}

textures/ncts_dm1/flameanim_blue
{
	qer_editorimage textures/sfx/b_flame1.tga
	q3map_lightimage textures/sfx/b_flame7.tga
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nolightmap
	nopicmip
	cull none
	q3map_surfacelight 1800
	{
		animMap 10 textures/sfx/b_flame1.tga textures/sfx/b_flame2.tga textures/sfx/b_flame3.tga textures/sfx/b_flame4.tga textures/sfx/b_flame5.tga textures/sfx/b_flame6.tga textures/sfx/b_flame7.tga textures/sfx/b_flame8.tga
		blendFunc GL_ONE GL_ONE
		rgbGen wave inverseSawtooth 0 1 0 10
	}	
	{
		animMap 10 textures/sfx/b_flame2.tga textures/sfx/b_flame3.tga textures/sfx/b_flame4.tga textures/sfx/b_flame5.tga textures/sfx/b_flame6.tga textures/sfx/b_flame7.tga textures/sfx/b_flame8.tga textures/sfx/b_flame1.tga
		blendFunc GL_ONE GL_ONE
		rgbGen wave sawtooth 0 1 0 10
	}	
	{
		map textures/sfx/b_flameball.tga
		blendFunc GL_ONE GL_ONE
		rgbGen wave sin .6 .2 0 .6	
	}
}

textures/ncts_dm1/rock_simple
{
  qer_editorimage textures/se_gothic/rock.tga
	{
 		map $lightmap
 		rgbGen identity
 	}
 	{
 		map textures/se_gothic/rock.tga
 		blendfunc filter
 	}
}

textures/ncts_dm1/rock_simple2
{
	qer_editorimage textures/ct_infinity/rock_01.tga
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

textures/ncts_dm1/item_decal_armor_silver
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/ncts_dm1/item_decal_armor_silver.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_armor.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/ncts_dm1/item_decal_gl_silver
{
	qer_editorimage textures/ncts_dm1/item_decal_gl_silver.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/ncts_dm1/item_decal_gl_silver.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_gl.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/ncts_dm1/item_decal_lg_silver
{
	qer_editorimage textures/ncts_dm1/item_decal_lg_silver.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/ncts_dm1/item_decal_lg_silver.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_lg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/ncts_dm1/item_decal_mh_silver
{
	qer_editorimage textures/ncts_dm1/item_decal_mh_silver.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/ncts_dm1/item_decal_mh_silver.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_mh.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/ncts_dm1/item_decal_pg_silver
{
	qer_editorimage textures/ncts_dm1/item_decal_pg_silver.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/ncts_dm1/item_decal_pg_silver.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_pg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/ncts_dm1/item_decal_rg_silver
{
	qer_editorimage textures/ncts_dm1/item_decal_rg_silver.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/ncts_dm1/item_decal_rg_silver.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_rg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/ncts_dm1/item_decal_rl_silver
{
	qer_editorimage textures/ncts_dm1/item_decal_rl_silver.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/ncts_dm1/item_decal_rl_silver.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_rl.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/ncts_dm1/item_decal_sg_silver
{
	qer_editorimage textures/ncts_dm1/item_decal_sg_silver.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/ncts_dm1/item_decal_sg_silver.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_sg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/ncts_dm1/ncts_jp_fx
{
	surfaceparm nodamage
  	surfaceparm nomarks
  	surfaceparm nolightmap
	surfaceparm nonsolid
  	surfaceparm	trans
	q3map_surfacelight 600
	nopicmip
	{
		clampmap textures/ncts_dm1/ncts_jp_fx.tga
		blendFunc GL_ONE GL_ONE
		tcMod rotate 75
	}
}

textures/ncts_dm1/ncts_jp_fx2
{
	qer_editorimage textures/ncts_dm1/ncts_jp_fx2.tga
	q3map_surfacelight	300
	nopicmip
	surfaceparm	trans
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm nonsolid
	cull none
	polygonoffset
	{
		clampmap textures/ncts_dm1/ncts_jp_fx2.tga
		blendfunc add
		tcMod rotate 100
	} 	
}

textures/ncts_dm1/silver_flag_long
{
    tessSize 64
    deformVertexes wave 194 sin 0 3 0 .4
    deformVertexes normal .5 .1
    surfaceparm nomarks
	surfaceparm nonsolid
    cull none
	{
		map textures/ncts_dm1/silver_flag_long.tga
		blendfunc blend
		rgbGen identity
	}
	{
		map $lightmap
		blendfunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

textures/ncts_dm1/silver_flag_short
{
	tessSize 64
    deformVertexes wave 194 sin 0 3 0 .4
    deformVertexes normal .5 .1
    surfaceparm nomarks
    cull none
	{
		map textures/ncts_dm1/silver_flag_short.tga
		blendfunc blend
		rgbGen identity
	}
	{
		map $lightmap
		blendfunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

textures/ncts_dm1/concrete_grass
{
	qer_editorimage textures/ql/concrete_brown.tga
	{
		map textures/ql/concrete_brown.tga
		rgbGen identity
	}
	{
		map textures/phantgothic/phantgothic_grass_001.jpg
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		alphaGen vertex
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/ncts_dm1/tile_01
{
	qer_editorimage textures/se_gothic/tile_01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/se_gothic/tile_01.tga
		tcmod scale 1 1
		blendfunc filter
	}
}

textures/ncts_dm1/jp1
{
	qer_editorimage textures/ncts_dm1/steptread2_16.tga
	surfaceparm nomarks
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ncts_dm1/steptread2_16.tga
		blendfunc filter
	}
}

textures/ncts_dm1/jp2
{
	qer_editorimage textures/ncts_dm1/stepriser2_8.tga
	surfaceparm nomarks
	nopicmip
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/ncts_dm1/stepriser2_8.tga
		blendfunc filter
	}
}