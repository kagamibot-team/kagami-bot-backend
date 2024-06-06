import PIL
import PIL.Image
import cv2


PillowColorLikeStrong = str | int | tuple[int, int, int] | tuple[int, int, int, int] | None
PillowColorLike = int | tuple[int] | tuple[int, int] | tuple[int, int, int] | tuple[int, int, int, int] | str | float | tuple[float]
PillowColorLikeWeak = PillowColorLike | None

PILImage = PIL.Image.Image
Cv2Image = cv2.typing.MatLike
