from setuptools import setup

setup(
        name="nicole",
        version="2.0",
        description="Write lyrics from genius or azlyrics.com to a mp3-tag",

        author="Matthias Quintern",
        author_email="matthiasqui@protonmail.com",

        url="https://github.com/MatthiasQuintern/nicole.git",

        license="GPLv3",

        packages=["nicole"],
        install_requires=["mutagen", "beautifulsoup4"],

        classifiers=[
            "Operating System :: POSIX :: Linux",
            "Environment :: Console",
            "Programming Language :: Python :: 3",
            "Topic :: Multimedia :: Audio",
            "Topic :: Utilities",
            ],

        # scripts=["bin/nicole"],
        entry_points={
            "console_scripts": [ "nicole=nicole.nicole:main" ],
            },
)
