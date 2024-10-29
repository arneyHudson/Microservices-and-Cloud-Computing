-- Create the portfolio database
CREATE DATABASE IF NOT EXISTS portfolio;

USE portfolio;

-- Drop the existing projects table if it exists
DROP TABLE IF EXISTS projects;

-- Create the projects table with additional fields for detailed project information
CREATE TABLE IF NOT EXISTS projects (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  TITLE VARCHAR(255) NOT NULL,
  DATE_RANGE VARCHAR(255) NOT NULL,
  ASSOCIATED_WITH VARCHAR(255) NOT NULL,
  BACKGROUND TEXT NOT NULL,
  PROJECT_GOAL TEXT NOT NULL,
  SKILLS TEXT NOT NULL
);

-- Insert detailed project information into the projects table
INSERT INTO projects (
  TITLE,
  DATE_RANGE,
  ASSOCIATED_WITH,
  BACKGROUND,
  PROJECT_GOAL,
  SKILLS
) VALUES
-- Project 1: Generative AI Piano
('Generative AI Piano',
 'Jan 2024 - Present',
 'Milwaukee School of Engineering',
 'Supported by Direct Supply and the ITC.',
 'Allow users to input text describing desired music, outputting to a self-playing piano. Conducted initial meetings to define team roles. Gathered extensive data from various music genres (classical, pop, rock, etc.). Engineered features by adding text descriptions to MIDI files using the OpenAI API. Planned to train a model to build custom MIDI files from text using the supercomputer ROSIE.',
 'BERT, LLM, Data Collection, NLP, Deep Learning, Transformer Models'),

-- Project 2: Customer Clustering from Sales Information
('Customer Clustering from Sales Information',
 'Jan 2024 - May 2024',
 'Milwaukee School of Engineering',
 'Supported by the Data Science Team at Scot Forge.',
 'Identify customer clusters from business and sales data. Led meetings to divide work among team members. Cleaned and aggregated data from six databases into a unified table. Engineered features, moving categorical columns to numerical and adding time series elements. Imputed missing values using a KNN Imputer. Web scraped longitude and latitude coordinates using OpenStreetMaps API. Researched clustering methods (Fuzzy, DBScan) and tested with our dataset. Created a pipeline for retrieving the final aggregated dataset. Developed scripts to test feature combinations in clustering algorithms. Participated in team presentations and talks.',
 'Data Visualization, Team Management, Cluster Analysis, Statistical Data Analysis, Data Science'),

-- Project 3: Full Stack Development of the game Wordle
('Full Stack Development of the game Wordle',
 'Mar 2023 - May 2023',
 'Milwaukee School of Engineering',
 'Collaborated with team members to implement classes and GUI components using Java and JavaFX.',
 'Followed an iterative development approach, delivering a working version in each sprint. Facilitated regular feedback and communication for project alignment. Divided tasks into manageable units for efficient completion. Ensured high-quality outcomes through continuous testing and integration. Addressed technical debt to maintain code quality.',
 'Teamwork, UX, Git, Sprints, Java, JUnit Tests, JavaFX, Full-Stack Development, OOP, Agile Methodologies, Front-End Development');
