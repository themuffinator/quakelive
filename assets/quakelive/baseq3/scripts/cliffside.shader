textures/q3adm02_sky/q3adm02_sky
{
	qer_editorimage textures/q3adm02_sky/env/q3adm02_up.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	nopicmip
	q3map_globaltexture
	skyParms textures/q3adm02_sky/env/q3adm02 1500 -
	q3map_sunExt 1 1 .7 261 -161 60 2 12
	q3map_skyLight 125 3
	{
		map textures/q3adm02_sky/q3adm02_clouds.tga
		blendfunc blend
		rgbGen identityLighting
		tcMod scroll 0.0215 -0.0155
	}
	{
		map textures/q3adm02_sky/q3adm02_horizon.tga
		blendfunc gl_one_minus_src_alpha gl_src_alpha
		rgbGen identityLighting
		tcMod transform 0.25 0 0 0.25 0.1075 0.1075
	}
}

textures/q3adm02_sky/q3adm02_fog
{
	qer_editorimage textures/q3adm02_sky/env/q3adm02_dn.tga
	qer_trans 0.70
	surfaceparm fog
	surfaceparm nodrop
	surfaceparm nolightmap
	surfaceparm nonsolid
	surfaceparm trans
	q3map_globaltexture
	fogparms ( 0.776471 0.776471 0.776471 ) 1799
}

textures/q3adm02_sky/q3adm02_godray
{
	surfaceparm nolightmap
	surfaceparm trans
	cull disable
	deformVertexes autosprite2
	qer_trans 0.70
	{
		map textures/q3adm02_sky/q3adm02_godray.tga
		blendfunc add
		rgbGen identity
	}
}

textures/q3adm02_sky/q3adm02_skyflare
{
	surfaceparm nolightmap
	surfaceparm trans
	cull disable
	deformVertexes autosprite
	qer_trans 0.70
	{
		map textures/q3adm02_sky/q3adm02_skyflare.tga
		blendfunc add
		rgbGen identity
	}
}

textures/q3adm02_sky/q3adm02_skylight1
{
	surfaceparm nolightmap
	surfaceparm trans
	cull disable
	qer_trans 0.70
	{
		map textures/q3adm02_sky/q3adm02_skylight1.tga
		blendfunc add
		rgbGen identity
	}
}

textures/q3adm02_sky/q3adm02_skylight2
{
	surfaceparm nolightmap
	surfaceparm trans
	cull disable
	qer_trans 0.70
	{
		map textures/q3adm02_sky/q3adm02_skylight2.tga
		blendfunc add
		rgbGen identity
	}
}