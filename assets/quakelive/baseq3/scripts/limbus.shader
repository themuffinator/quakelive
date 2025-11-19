textures/map_limbus/Limbus_sky
{
	qer_editorimage textures/skies/meth_clouds.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	surfaceparm nodlight

	q3map_sun 0.505882 0.745098 0.968627 120 120 80
	q3map_surfacelight 80

	q3map_lightmapSampleSize 32

	q3map_lightImage textures/skies/meth_clouds.tga
	skyparms - 512 -
	{
		map textures/skies/meth_clouds2.tga
		tcMod scale 10 10
		tcMod scroll .1 .1
	}
	{
		map textures/skies/topclouds.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 3 3
		tcMod scroll 0.09 0.09
	}
}

textures/map_limbus/Limbus_blueJP
{      
	qer_editorimage textures/sfx2/jumpad03.tga 
	nopicmip        
	{
		map textures/map_limbus/blueJPswirl.tga
		blendFunc GL_ONE GL_ZERO
		tcmod rotate 130
		//tcMod stretch sin .7 0.5 0 .2
		rgbGen identity
	}
	{
		map textures/sfx2/fan01.tga
		blendFunc blend
		tcmod rotate -311
		rgbGen identity
	}
	{
		clampmap textures/map_limbus/blueJPthrob.tga
		blendfunc Add
		tcmod rotate 130
		tcMod stretch sin 1.2 .8 0 1.4
		rgbGen wave square .5 .5 .25 1.4
	}
	{
		map textures/sfx2/jumpad03.tga
		blendFunc blend
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ONE_MINUS_DST_ALPHA
		rgbGen identity
	}
}

textures/map_limbus/item_decal_armor_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_armor_brown.tga
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

textures/map_limbus/item_decal_gl_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_gl_brown.tga
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

textures/map_limbus/item_decal_lg_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_lg_brown.tga
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

textures/map_limbus/item_decal_mh_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_mh_brown.tga
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

textures/map_limbus/item_decal_pg_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_pg_brown.tga
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

textures/map_limbus/item_decal_regen_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_regen_brown.tga
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

textures/map_limbus/item_decal_rg_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_rg_brown.tga
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

textures/map_limbus/item_decal_rl_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_rl_brown.tga
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

textures/map_limbus/item_decal_quad_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_quad_brown.tga
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

textures/map_limbus/item_decal_sg_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_sg_brown.tga
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

textures/map_limbus/item_decal_bs_brown
{
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse

	{
		map textures/map_limbus/item_decal_bs_brown.tga
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
		map textures/map_limbus/item_decal_bs.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}