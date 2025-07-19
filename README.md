# 1A Code Concept & Installation Process Walkthrough by team CODDIIII

In 1A the requirement is to upload a file & then show output in JSON format where in that JSON file the data will be as **Title , Headings: H1, H2, H3 (with level and page number)** . Inorder to achieve this we've made a model following algo of logistic regression.

## Work Flow

- First the pdf texts get extracted through **PDF PLUMBER**(a package) & stores in a CSV file then the work of model starts.

What the model does❓

- It first reads the CSV file that **PDF Plumber** generated & extracts the texts based on their **avg font size perpage, capital letters, bullet points, realtive fontsize, whether a title etc.**

- After that it converts the extracted data into a CSV file & then the data is shown as JSON.


## Installation

To run this project locally you've to do the following :

**First fork the repo**

```bash
  git clone https://github.com/Siddharthcoding/Team_CODDIIII_1A_Repo.git
```

To install the packages run the below command :

```bash
 pip install -r requirements.txt
```

**!! Installing packages is a must otherwise the model won't work !!**   

Inorder to generate headers from one's pdf the user have to move the pdf into the **input** directory. 

After moving the pdf to the **input** directory user have to run the below command in the terminal.

```bash
  python process_pdf.py --pdf filename.pdf 
```

**where filename.pdf will be replaced by the file that user will move to the input directory**

The user can watch the output in json form which will look like something below:

```bash
  {
  "title": "Revised January 10, 2014",
  "outline": [
    {
      "level": "H1",
      "text": "Revised January 10, 2014",
      "page": 1,
      "children": []
    },
    {
      "level": "H1",
      "text": "JUDICIAL INTERN HIRING INFORMATION",
      "page": 1,
      "children": []
    },
    {
      "level": "H1",
      "text": "Lorna G. Schofield, United States District Judge",
      "page": 1,
      "children": []
    },
    {
      "level": "H1",
      "text": "Chambers Contact Information:",
      "page": 1,
      "children": []
    },
    {
      "level": "H1",
      "text": "United States District Court",
      "page": 1,
      "children": []
    },
    {
      "level": "H1",
      "text": "Southern District of New York",
      "page": 1,
      "children": []
    },
    {
      "level": "H1",
      "text": "40 Centre Street, Room 201",
      "page": 1,
      "children": []
    },
    {
      "level": "H1",
      "text": "New York, NY 10007",
      "page": 1,
      "children": []
    },
    {
      "level": "H1",
      "text": "(212) 805-0288",
      "page": 1,
      "children": []
    },
    {
      "level": "H1",
      "text": "time for at least eight weeks.",
      "page": 1,
      "children": []
    }
  ]
}
```

The output will be in **output** directory as filename.json
