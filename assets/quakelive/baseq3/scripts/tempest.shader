textures/ql/grate_01
{
   	surfaceparm nonsolid
	surfaceparm nomarks	
    nopicmip
	qer_editorimage textures/ql/grate_01.tga
	{
		map textures/ql/grate_01.tga
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

textures/decals/decal_01
{
   noPicMip
   polygonOffset
   surfaceparm nonsolid
   surfaceparm nomarks
   {
      map textures/decals/decal_01.tga
      blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
   }
}

textures/decals/decal_02
{
   noPicMip
   polygonOffset
   surfaceparm nonsolid
   surfaceparm nomarks
   {
      map textures/decals/decal_02.tga
      blendFunc GL_ZERO GL_ONE_MINUS_SRC_COLOR
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

textures/sfx/blackfog_longdist
      {
              qer_editorimage textures/ct_infinity/black.tga
              surfaceparm fog
              surfaceparm nonsolid
              surfaceparm trans
              surfaceparm nolightmap
			  qer_trans 0.5
              qer_nocarve
              fogparms ( 0 0 0 ) 4000
      }
	  
textures/base_light/yellow_light
{
	surfaceparm nomarks
	qer_editorimage textures/base_light/lamp_01_yellow.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/lamp_01_yellow.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/lamp_01_yellow_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}