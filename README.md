## Rune Project

This project explores runestones using machine learning techniques to analyze and classify them, paired with an interactive map that visualizes their geographical locations. The data is integrated into Power BI for  visualizations, including coordinates of runestones, allowing for insights into their distribution.


## Features

- 📊 Machine Learning Analysis:
    - Classification and clustering of runestones based on features such as age and origin


- 🗺️ Interactive Map:
    - Visualization of runestone locations on a map with Power BI 
    - Drill down to specific coordinates for detailed information on individual artifacts.

- 📍 Runestone Coordinates:
    - Each runestone is linked to its GPS coordinates, enabling researchers and enthusiasts to explore their physical locations.


## How It Works

1. Data Collection:

- The project starts by gathering a dataset of runestones, inscriptions and geographical information (GPS coordinates).

2. Machine Learning:

- Preprocessing: Clean and preprocess the textual inscriptions.

- NLP Analysis: Apply machine learning algorithms to classify runestone inscriptions

- Modeling: Use algorithms such as Logistic Regression, Support Vector Classifier (SVC) to analyze and classify the runestones.

3. Interactive Map:

- Use Power BI to create an interactive dashboard.

## Installation

To set up this project locally:

1. Clone the Repository
Start by cloning the repository to your local machine. This step allows you to access all files needed for the project, including datasets, scripts, and the Power BI visualization template.

```bash
git clone https://github.com/Jesper0101/Runskrift.git
cd Runskrift
```

2. Machine Learning Model Setup
The repository includes machine learning scripts that analyze and classify runestone inscriptions. To run these models, ensure that you have Python 3.12 and the required Python libraries installed. These libraries, such as pandas and scikit-learn, handle data processing, machine learning, and visualization.

You can install the libraries using:

```bash
pip install pandas scikit-learn matplotlib numpy sqlalchemy requests chardet xlrd
```
Then, execute the machine learning scripts to begin processing and analyzing the runestone data.


3. Power BI Setup:

- Ensure you have Power BI Desktop installed. You can download it [here](https://powerbi.microsoft.com/desktop/).
- Open the provided Power BI folder and then run the Power BI file called (Rundata.pbix).


4. Data Visualization:

- Upload the cleaned dataset into Power BI.
- Use the pre-built dashboard to visualize the runestone locations and coordinate-based insights.
## Requiermemts

- Python 3.12

- Power BI

- Libraries
    - Pandas, scikit-learn, matplotlib, numpy, sqlalchemy, requests, chardet, xlrd

## Authors

- [@Mac-u-ser](https://github.com/Mac-u-ser)
- [@Jesper0101](https://github.com/Jesper0101)
- [@Julia-xiaoyong-Yang](https://github.com/Julia-xiaoyong-Yang)
- [@GoranSkejo](https://github.com/GoranSkejo)
- [@KhaldounAgha](https://github.com/KhaldounAgha)
