
#pragma once

#if defined(DX_TO_VK_ABSTRACTION)

#include <d3d9.h>
#include "togl/dxabstract.h"
#include "togl/dxabstract_types.h"

typedef HWND VD3DHWND;
typedef HWND VD3DHANDLE;

#else

#ifdef WIN32
#ifdef _X360
#include "d3d9.h"
#include "d3dx9.h"
#else
#include <windows.h>
#include "../../dx9sdk/include/d3d9.h"
#include "../../dx9sdk/include/d3dx9.h"
#endif
#endif

typedef HWND VD3DHWND;

#endif // defined(DX_TO_VK_ABSTRACTION)

#define	GLMPRINTF(args)	
#define	GLMPRINTSTR(args)
#define	GLMPRINTTEXT(args)
