# ✈️ Airline Reviews - Reddit Data Pipeline & Dashboard

This project is a FastAPI-powered pipeline to collect airline-related posts from Reddit and analyze them using Power BI.  
It is designed to support real-time applications for sentiment analysis and customer feedback tracking in the airline industry.

---

##  Project Overview

This repository is divided into the following phases:

###  Phase 1: Data Collection & Exploration
- Built with **FastAPI** + **PRAW** to fetch Reddit posts using Reddit’s API.
- Filters airline-related posts based on keywords.
- Stores cleaned JSON files for each airline and exports a unified `.csv` for Power BI analysis.


###  Phase 2: Sentiment Classification & Live App ( Next steps ) 
- Train a **machine learning model** to classify sentiment (positive/neutral/negative).
- Build a **real-time app** to track live Reddit mentions and sentiment per airline.
- Deploy a frontend to allow public interaction with the data in real-time.

---

##  Sample Dashboard (Power BI)

![image](https://github.com/user-attachments/assets/5a4ba975-9364-4db4-9bfc-730542fbc18f)


> 🔎 **Note:** This dashboard is built to validate data quality and analysis logic before integrating machine learning.



## ⚙️ Technologies Used

| Tool        | Purpose                                |
|-------------|----------------------------------------|
| FastAPI     | API backend for Reddit scraping        |
| PRAW        | Python Reddit API Wrapper              |
| Power BI    | Data visualization & dashboarding      |
| Pandas      | Data cleaning and transformation       |
| dotenv      | Manage environment variables securely  |

---

## 🧪 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/niinog/Airline_Reviews.git
cd Airline_Reviews
