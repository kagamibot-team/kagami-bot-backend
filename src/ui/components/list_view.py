import PIL
import PIL.Image

from src.ui.base.basics import Fonts, pile, render_text, vertical_pile
from src.ui.components.awards import ref_book_box
from src.ui.views.list_view import ListView, ListViewDocument, TitleView


def render_list_view(element: ListView, columns: int) -> PIL.Image.Image:
    images: list[PIL.Image.Image] = []

    for e in element.awards:
        images.append(ref_book_box(e))

    return pile(
        images,
        paddingX=0,
        paddingY=0,
        columns=columns,
        background="#9B9690",
        horizontalAlign="top",
        verticalAlign="left",
        marginLeft=30,
        marginRight=30,
        marginBottom=30,
        marginTop=0,
    )


def render_document(document: ListViewDocument) -> PIL.Image.Image:
    images: list[PIL.Image.Image] = []

    for e in document.docs:
        if isinstance(e, str):
            e = TitleView(title=e)
        if isinstance(e, TitleView):
            images.append(
                render_text(
                    text=e.title,
                    font_size=e.size,
                    font=[Fonts.HARMONYOS_SANS_BLACK, Fonts.MAPLE_UI],
                    color=e.color,
                    width=document.inner_width,
                )
            )
        if isinstance(e, ListView):
            images.append(render_list_view(e, document.columns))

    return vertical_pile(
        images,
        paddingY=15,
        background="#9B9690",
        marginTop=60,
        marginLeft=60,
        marginRight=60,
        marginBottom=60,
    )
