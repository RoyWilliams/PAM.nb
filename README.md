# PAM.nb: Python notebooks for grant managers
## View your University of Edinburgh grants beyond People and Money

This set of notebooks and supporting code is designed to help a grant manager deal with the 
University of Edinburgh [People and Money](https://www.ed.ac.uk/staff/services-support/hr-and-finance/people-and-money-system) system. 

If I am a user of this code, then I am assumed to have 
(1) A team of *people* whose salaries come from the grants that I manage, and
(2) A number of *grants*, each employing team-members and buying things.

I want to see where the money has gone in the past and to plan for the future with forecasting. 
You will need two types of file from the People and Money system:
- transactions.xlsx: an Excel file with all the transactions on your grants, both salary and other spending.
- project.xls: an Excel file listing your grants (or projects) with the amount of the award split into categories.

The PAM.nb notebooks and code are organised around these concepts:

- A **run** is a period of time for the analysis to cover. The beginning of the run must be in the past, 
and the end in the future. Times are written, for example `Aug-22`.

- A **person** has a surname and cost per month. 

- A **grant** is a combination of information supplied by the grant manager, with data from P&M.

- Grants are **assigned** to people on a month to month basis. For example Bloggs can be paid from the 
ComfortIV grant from October 22 with this line:
`["Bloggs",    "ComfortIV",             "Oct-22", 0.5],`

The People, Grants, and Assignment is done by the grant manager making JSON files. 
There are examples in the `toydata` and `toydata2` directories. 
There is a useful online tool [jsonlint](https://jsonlint.com) that helps with formatting JSON files.

There are three notebooks; the HTML preview is linked:
- **[Readme](https://htmlpreview.github.io/?https://raw.githubusercontent.com/RoyWilliams/PAM.nb/main/Readme.html)**
This is an introduction to the PAM.nb system. First point it to the correct data directory, then it will read and check your files.

- **[Grants](https://htmlpreview.github.io/?https://raw.githubusercontent.com/RoyWilliams/PAM.nb/main/Grants.html)**
This is a listing of all the grants, each with graphs and tables defining where the money has gone, 
and the futureconsequences of the assignment of people to grants.

- **[People](https://htmlpreview.github.io/?https://raw.githubusercontent.com/RoyWilliams/PAM.nb/main/People.html)**
Each team member is shown with the composition of their salary from the various grants. You can check that each person 
is at the correct level -- 100% for full time or 60% for part time.
