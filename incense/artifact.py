import pickle
import os
from IPython.display import HTML
from IPython import display
import pandas as pd
import warnings
from copy import copy


class Artifact:
    """Displays or saves an artifact."""

    can_render = tuple()

    def __init__(self, name: str, file, content_type: str = None):
        self.name = name
        self.file = file
        self.content_type = content_type
        self.extension = None if self.content_type is None else self.content_type.split("/")[-1]
        self._content = None
        self._rendered = None

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name})'

    def render(self):
        """Render the artifact according to its content-type."""
        if self._rendered is None:
            self._rendered = self._render()
        return self._rendered

    def _render(self):
        """Return the object that represents the rendered artifact."""
        raise NotImplementedError

    def show(self):
        warnings.warn("`show` is deprecated in favor of `render` and will removed in a future release.",
                      DeprecationWarning,
                      stacklevel=2)
        return self.render()

    def save(self, save_dir: str = ''):
        """Save artifact to disk."""
        with open(os.path.join(save_dir, self._make_filename()), 'wb') as file:
            file.write(self.content)

    def as_content_type(self, content_type):
        """Interpret artifact as being of content-type."""
        try:
            artifact_type = content_type_to_artifact_cls[content_type]
        except KeyError:
            raise ValueError(f'Incense does not have a class that maps to content-type {content_type}')
        else:
            return self.as_type(artifact_type)

    def as_type(self, artifact_type):
        self.file.seek(0)
        return artifact_type(self.name, self.file)

    @property
    def content(self):
        """Access the raw bytes of the artifact."""
        if self._content is None:
            self._content = self.file.read()
        return self._content

    def _make_filename(self):
        parts = self.file.filename.split('/')
        return f'{parts[-2]}_{parts[-1]}.{self.extension}'


class ImageArtifact(Artifact):
    """Displays or saves an image artifact."""

    can_render = ('image/png', 'image/jpeg')

    def _render(self):
        return display.Image(data=self.content)


class MP4Artifact(Artifact):
    """Displays or saves a MP4 artifact"""

    can_render = ("video/mp4",)

    def _render(self):
        self.save()
        return HTML(f"""
        <video width="640" height="480" controls autoplay>
          <source src="{self._make_filename()}" type="video/mp4">
        </video>
        """)


class CSVArtifact(Artifact):
    """Displays and saves a CSV artifact"""

    can_render = ("text/csv",)

    def _render(self):
        return pd.read_csv(self.file)


class PickleArtifact(Artifact):
    """Displays and saves a Pickle artifact"""

    can_render = tuple()

    def __init__(self, name: str, file, content_type: str = None):
        super().__init__(name, file, content_type)
        self.extension = "pickle"

    def _render(self):
        return pickle.load(self.file)


class PDFArtifact(Artifact):
    """Displays and saves a PDF artifacts."""
    can_render = ("application/pdf",)

    # TODO probably needs jupyter extension to be able to display pdf.
    # def _render(self):
    #     return IFrame(self._make_filename(), width=600, height=300)
    #


content_type_to_artifact_cls = {}
for cls in copy(locals()).values():
    # print(cls)
    if isinstance(cls, type) and issubclass(cls, Artifact):
        for content_type in cls.can_render:
            content_type_to_artifact_cls[content_type] = cls

# print(content_type_to_artifact_cls)
