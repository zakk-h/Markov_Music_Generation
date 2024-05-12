# Markov Music Generator

This project utilizes Markov Chains to automate the generation of unique musical sequences, both rhythmic and melodic, based on predefined difficulty levels and musical constraints. It provides a flexible and customizable approach to music creation, making it useful for creating varied musical pieces for practice and entertainment.

## Features

- **Rhythmic Pattern Generation:** Generates complex rhythmic sequences adjustable by difficulty levels, ideal for sightreading practice for percussionists.
- **Pitch Sequence Generation:** Creates melodic contours that accompany the rhythmic structures, suitable for melodic instrument sightreading practice.
- **Time Signature Flexibility:** Supports multiple time signatures to enhance the diversity of the music produced.
- **Customizable Difficulty Level:** This feature enables adjusting the range in pitch, leaps, and complexity of rhythms, either by exclusion or with reduced likelihood.
- **LilyPond Integration:** Uses LilyPond to notate and visualize the generated music, providing clear and professional-looking sheet music.
- **Caching System:** Efficiently caches computed matrices for rapid music generation, using pickle with gzip compression for storage efficiency.

## Getting Started

### Prerequisites

You will need the following packages:

```bash
pip install numpy
```

Additionally, this project requires [LilyPond](http://lilypond.org/) for music notation. Please follow the installation instructions on their website to install LilyPond on your system.

### Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/zakk-h/Markov_Music_Generation
cd Markov_Music_Generation
