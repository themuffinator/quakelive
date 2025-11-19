textures/mrcq3t4/mrcq3t4sky
{
	qer_editorimage textures/mrcq3t4/mrcblugrysky.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 256 
	q3map_sun	.806 .75 .806 60 60 85
	q3map_surfacelight 30

	skyparms - 512 -
	
	{
		map textures/mrcq3t4/mrcblugrysky.tga
		tcMod scale 2 2
		tcMod scroll -0.005 0.005
		depthWrite
	}
	{
		map textures/mrcq3t4/stmcloudgry.tga
		blendfunc gl_dst_color gl_one
		tcMod scale 2 2
		tcMod scroll -0.03 -0.01
		rgbgen identity
	}
}
textures/mrcq3t4/prophecy_sky
{
	qer_editorimage textures/mrcq3t4/prophecy_q3r.tga
        surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	q3map_lightsubdivide 256
	q3map_sun	.925 .906 .698 55 60 85
	q3map_surfacelight 15

        skyparms env/prophecy 512 -

	
}

textures/mrcq3t4/sand_02
{
	qer_editorimage textures/mrcq3t4/sand_02.tga
	surfaceparm nosteps
	{
		map $lightmap
		rgbGen identity

	}
	{
		map textures/mrcq3t4/sand_02.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbgen identity
	}
}
textures/mrcq3t4/sand_02_bloody
{
	qer_editorimage textures/mrcq3t4/sand_02_bloody.tga
	surfaceparm nosteps
	{
		map $lightmap
		rgbGen identity

	}
	{
		map textures/mrcq3t4/sand_02_bloody.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbgen identity
	}
}
textures/mrcq3t4/rustpent
{

	surfaceparm nodamage
	q3map_lightimage textures/sfx/jumppadsmall.tga	
	q3map_surfacelight 400

	
	{
		map textures/mrcq3t4/rustpent.tga
		rgbGen identity
	}
	
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}
	
	{
		clampmap textures/sfx/jumppadsmall.tga
		blendfunc add
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}

}
textures/mrcq3t4/3b3pent
{

	surfaceparm nodamage
	q3map_lightimage textures/sfx/jumppadsmall.tga	
	q3map_surfacelight 400

	
	{
		map textures/mrcq3t4/3b3pent.tga
		rgbGen identity
	}
	
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
	}
	
	{
		clampmap textures/sfx/jumppadsmall.tga
		blendfunc add
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}

}
textures/mrcq3t4/col_i_rune01_litx
{
	qer_editorimage textures/mrcq3t4/col_i_rune01_lit.tga
	q3map_surfacelight 50	
	q3map_lightimage textures/mrcq3t4/col_i_rune01_lit.blend.tga	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcq3t4/col_i_rune01_lit.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
	{
		map textures/mrcq3t4/col_i_rune01_lit.blend.tga
		blendfunc GL_ONE GL_ONE
		rgbgen wave sin 0.6 .4 0.6 0.2
	}
}
textures/mrcq3t4/col_i_rune04_litx
{
	qer_editorimage textures/mrcq3t4/col_i_rune04_lit.tga
	q3map_surfacelight 50	
	q3map_lightimage textures/mrcq3t4/col_i_rune04_lit.blend.tga	
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/mrcq3t4/col_i_rune04_lit.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
	{
		map textures/mrcq3t4/col_i_rune04_lit.blend.tga
		blendfunc GL_ONE GL_ONE
		rgbgen wave sin 0.6 .4 0.6 0.15
	}
}
