# STL2CAD

FreeCAD workbench that converts an STL, or the model on screen, into a STEP file.

It is free for FreeCAD users. [RAG Box](https://ragbox.llc/) sponsors it and is the place to get help. GAID (Guide AI Dev Pro) guides AI programming and was used to build this add-on.

## Install

After FreeCAD lists it, open **Tools → Addon Manager**, find **STL2CAD**, and install it. Then switch to the **STL2CAD** workbench.

FreeCAD 1.0 or newer.

## Use

1. Open a model, or leave the screen empty if you will upload an STL.
2. **Load STL** sends the model on screen. **Upload STL** picks a file.
3. Move the density slider if you want a coarser or finer mesh, then click **Convert**.
4. **Consider extrusions** is on by default. Turn it off if you do not like that result.
5. **Open viewer** shows the STL and the STEP. **Save STEP** writes the STEP file where you name it.

The add-on calls the converter at https://www.stl2cad.com. People who open that website on their own are using a separate product.

## License

LGPL-2.1-or-later. See `LICENSE`.
