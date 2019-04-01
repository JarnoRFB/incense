import pickle
import os
from io import BytesIO
import matplotlib.pyplot as plt
from IPython.display import HTML
import pandas as pd
import warnings


class Artifact:
    """Displays or saves an artifact."""

    extension = ""

    def __init__(self, name, file):
        self.name = name
        self.file = file
        self._content = None

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name})'

    def render(self):
        raise NotImplementedError

    def show(self):
        warnings.warn("`show` is deprecated in favor of `render` and will removed in a future release.", DeprecationWarning,
                      stacklevel=2)
        return self.render()

    def save(self, save_dir=''):
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
        if self._content is None:
            self._content = self.file.read()
        return self._content

    def _make_filename(self):
        parts = self.file.filename.split('/')
        return f'{parts[-2]}_{parts[-1]}.{self.extension}'


class PNGArtifact(Artifact):
    """Displays or saves a PNG artifact."""

    extension = "png"

    def __init__(self, name, file):
        super().__init__(name, file)
        self._img = None

    def render(self, figsize=(10, 10)):
        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(self.img)
        ax.axis('off')
        return fig

    @property
    def img(self):
        if self._img is None:
            self._img = plt.imread(BytesIO(self.content))
        return self._img


class MP4Artifact(Artifact):
    """Displays or saves a MP4 artifact"""

    extension = "mp4"

    def __init__(self, name, file):
        super().__init__(name, file)
        self.movie = None

    def render(self):
        if self.movie is None:
            self.movie = self._make_movie()
        return self.movie

    def _make_movie(self):
        self.save()
        return HTML(f"""
        <video width="640" height="480" controls autoplay>
          <source src="{self._make_filename()}" type="video/mp4">
        </video>
        """)


class CSVArtifact(Artifact):
    """Displays and saves a CSV artifact"""

    extension = "csv"

    def __init__(self, name, file):
        super().__init__(name, file)
        self.df = None

    def render(self):
        if self.df is None:
            self.df = self._make_df()
        return self.df

    def _make_df(self):
        df = pd.read_csv(self.file)
        return df


class PickleArtifact(Artifact):
    """Displays and saves a Pickle artifact"""

    extension = "pickle"

    def __init__(self, name, file):
        super().__init__(name, file)
        self.pyobject = None

    def render(self):
        if self.pyobject is None:
            self.pyobject = self._make()
        return self.pyobject

    def _make(self):
        obj = pickle.load(self.file)
        return obj


class PDFArtifact(Artifact):
    """Displays and saves a PDF artifacts."""
    extension = "pdf"

    # def __init__(self, name, file):
    #     print(super())
    #     super().__init__(name, file)
    #     self.pdf = None
    #
    # def render(self):
    #     if self.pdf is None:
    #         self.pdf = self._make_pdf()
    #     return self.pdf
    #
    # def _make_pdf(self):
    #     self.save()
    #     return IFrame(self._make_filename(), width=600, height=300)


content_type_to_artifact_cls = {
    'image/png': PNGArtifact,
    'text/csv': CSVArtifact,
    'video/mp4': MP4Artifact,
    'application/pdf': PDFArtifact
}
