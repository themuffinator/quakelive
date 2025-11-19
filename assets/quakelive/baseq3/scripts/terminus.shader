// smoothed grit/mud
textures/map_terminus/grit01_shadeangle_100
{
	q3map_nonplanar
	q3map_shadeangle 100
	qer_editorimage textures/proto2/grit01.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/proto2/grit01.tga
		blendFunc filter
	}
}

textures/map_terminus/terminus_glass01
{
	qer_editorimage textures/base_wall/shiny3.tga
	surfaceparm trans	
	cull disable
	qer_trans 0.5
	{
		map textures/effects/tinfx3.tga
		blendfunc add
		rgbGen identity
		tcGen environment 
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
	}
}

textures/map_terminus/pjgrate3
{
	qer_editorimage textures/base_floor/pjgrate2.tga
	surfaceparm metalsteps
	surfaceparm nomarks
	nopicmip	
	cull none
	
	// A RUSTED GRATE THAT CAN BE SEEN FROM BOTH SIDES
	// +NOMARKS
	{
		map textures/base_floor/pjgrate2.tga
		tcMod scale 2.0 2.0
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
		rgbGen identity
	}
}

textures/map_terminus/proto_fence_terminus
{
	qer_editorimage textures/base_trim/proto_fence.tga
	surfaceparm trans
	surfaceparm nomarks
	cull none
   nopicmip

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

textures/map_terminus/ceil1_34_nolight
{
	q3map_lightimage textures/base_light/ceil1_34.tga
	qer_editorimage textures/base_light/ceil1_34.tga
	surfaceparm nomarks
	//q3map_surfacelight 10000
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_34.tga
		blendFunc filter
		rgbGen identity
	}
}

textures/map_terminus/whitebeam
{
	qer_editorimage textures/common/white.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	q3map_surfacelight 200
	{
		map textures/common/white.tga
		blendFunc add
	}
}

textures/map_terminus/item_flare_QUAD
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_QUAD.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_terminus/item_flare_BS
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_BS.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_terminus/item_flare_RA
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_RA.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_terminus/item_flare_YA
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_YA.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_terminus/item_flare_MH
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_MH.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_terminus/item_flare_RG
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_RG.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_terminus/item_flare_PG
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_PG.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_terminus/item_flare_LG
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_LG.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_terminus/item_flare_RL
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_RL.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_terminus/item_flare_SG
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_SG.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_terminus/item_flare_GL
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_terminus/item_flare_GL.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}



textures/map_terminus/item_decal_armor_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_armor_brown.tga
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

textures/map_terminus/item_decal_gl_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_gl_brown.tga
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

textures/map_terminus/item_decal_lg_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_lg_brown.tga
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

textures/map_terminus/item_decal_mh_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_mh_brown.tga
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

textures/map_terminus/item_decal_pg_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_pg_brown.tga
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

textures/map_terminus/item_decal_regen_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_regen_brown.tga
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
		map textures/se_gothic/item_decal_regen.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_terminus/item_decal_rg_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_rg_brown.tga
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

textures/map_terminus/item_decal_rl_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_rl_brown.tga
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

textures/map_terminus/item_decal_quad_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_quad_brown.tga
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
		map textures/se_gothic/item_decal_quad.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_terminus/item_decal_sg_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_sg_brown.tga
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

textures/map_terminus/item_decal_bs_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_terminus/item_decal_bs_brown.tga
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
		map textures/map_terminus/item_decal_bs.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}