---
layout: post
title: "Streamlining Full-Text Article Retrieval for Research"
categories: tutorials
---
Welcome to the first in a series of short tutorials aimed at making LLM-powered applications more accessible for health and life sciences researchers. This tutorial introduces Python utility functions for interacting with the [OpenAlex API][how-to-use-the-openalex-api], a comprehensive, open-access catalog of global research named after the ancient Library of Alexandria and made by the nonprofit [OurResearch][ourresearch-url].

While other excellent [community libraries][openalexR] exist for querying the OpenAlex API, my focus here is on functions tailored for streamlining the retrieval of full-text articles indexed in PubMed and leveraging OpenAlex's extensive citation data. These features are particularly valuable for Retrieval-Augmented Generation (RAG) applications, which can enhance language model performance and improve response quality.

Check out the accompanying [Jupyter notebook][gh-nicomarr-public-tutorials] to run all examples described below. Note that we use [magic commands][ipython-readthedocs-magics] (%) or (!) to run shell commands within Jupyter notebooks.
<br>
<br>
<br>

### Installation and setup

(1) Install the required third-party libraries:
- requests
- tqdm
- selenium
- webdriver-manager
- nbformat
- plotly

In a Jupyter notebook environment, simply install these libraries using line magics and pip, like so:  
```
%pip install -qU requests
%pip install -qU tqdm
%pip install -qU selenium
%pip install -qU webdriver-manager
%pip install -qU nbformat
%pip install -qU plotly
```
<br>
<br>
(2) Download the file named `openalex_api_utils.py` from the following [GitHub repo][gh-nicomarr-public-tutorials], and save it to your working directory (e.g., the same directory from which you run the accompanying notebook). The `openalex_api_utils.py` file contains all utility functions described below and in the accompanying notebook.

In Colab or any other Jupyter notebook environment:
```
!wget -q https://raw.githubusercontent.com/nicomarr/public-tutorials/main/openalex_api_utils.py
```

Or in a terminal emulator:
```
wget https://raw.githubusercontent.com/nicomarr/public-tutorials/main/openalex_api_utils.py
```

If `wget` is not installed, you may also use curl:
```
curl -O https://raw.githubusercontent.com/nicomarr/public-tutorials/main/openalex_api_utils.py
```
<br>
<br>
(3) Import the utility functions:

{% highlight python %}
from openalex_api_utils import *
{% endhighlight %}
<br>
<br>
(4) Add your email address to the environment variables. In Google Colab, open the side panel, click on the 'key' icon and add a key-value pair with the key 'EMAIL' (all UPPERCASE, no dash) and your email address as the value, then enable notebook access. See the section below and [this link][colab-secrets] for more details. Your email address is sent as part of the request to the OpenAlex API. This is a common and polite practice that helps speed up response times when making many API calls. It also helps developers contact you if there are any issues. For more details, follow [this link][how-to-use-the-openalex-api].
<br>
<br>
(5) Load your email address from the environment variables. In Google Colab, you can do that by running the following commands after you have added your email address in the Secrets tab, as described above.

{% highlight python %}
from google.colab import userdata
EMAIL = userdata.get("EMAIL")
{% endhighlight %}

If you work with in a Jypyter notebook environment on your local computer, you can import environment variables using the os module:
{% highlight python %}
import os
EMAIL = os.environ["EMAIL"]
{% endhighlight %}

Alternatively, you may also just define it directly, like so:

{% highlight python %}
EMAIL = "REPLACE_WITH_YOUR_EMAIL@example.com"
{% endhighlight %}

However, it is best practice to keep sensitive information like email addresses out of the code.
<br>
<br>
<br>

### Basic usage

First, create a list containing unique identifyers of the works to retrieve information about. In OpenAlex, works can be PubMed articles, books, datasets, and theses. In this tutorial, we first get information about 3 PubMed articles using a unique identifyer for each article. Unique identifyers can be an OpenAlex ID, a PubMed ID (PMID), or a Digital Object Identifier (DOI).

{% highlight python %}
uids = ['https://openalex.org/W4387665659', '33497357', '10.1126/sciimmunol.aau8714']
{% endhighlight %}
<br>
<br>
The first utility function we will be using is `get_works()`. Here, we pass in as argument the list with the unique identifiers, and the email address we have imported from the environment variables. Note that DOIs are accepted with or without a `https://doi.org/` prefix, and OpenAlex IDs are accepted with or without a `https://openalex.org/` prefix. We can also set a third (optional) argument, `show_progress=True`, to show a progress bar. The function returns two list objects. The first list object (which we will name 'works') contains all the information retrieved from the OpenAlex API. The second list object contains only messages in case anything goes wrong, for example, if one or more IDs provided do not exist in the database. If everything is fine, this list will be empty.

{% highlight python %}
works, failed_calls = get_works(ids=uids, email=EMAIL, show_progress=True)
print("All works were successfully retrieved.") if len(failed_calls) == 0 else print("Some of the works could not be retrieved.")
{% endhighlight %}

***Output:***
```
Retrieving works: 100%|██████████| 3/3 [00:01<00:00,  1.92it/s]
All works were successfully retrieved.
```
<br>
<br>
We can access the retrieved metadata simply by indexing into the works object, which is a list of dictionaries. The data obtained from the OpenAlex API is stored under the key 'metadata'.
The next line prints the title of the first work in the list (for those new to Python, indexing starts at 0).

{% highlight python %}
print(works[0]['metadata']['title'])
{% endhighlight %}

***Output:***
```
Harnessing large language models (LLMs) for candidate gene prioritization and selection
```
<br>
<br>
To list all the works succesfully retrieved, we can use the `list_works()`function. This will display selected metadata of the retrieved articles in html format, including first author, title, journal, publication year, how many times it has been cited, the number of references, and 10 related works (which can also be retrieved from the OpenAlex API). Note that the symbols in the output indicate whether the article is open access or not, and whether the full text is available or not.

{% highlight python %}
list_works(works)
{% endhighlight %}

***Output (html):***
```
Toufiq et al. Harnessing large language models (LLMs) for candidate gene prioritization and selection. Journal of Translational Medicine 2023
Cited by: 10 | References: 64 | Related works: 10
Download PDF   Read Full Text   🔓   📖
 
Khan et al. Distinct antibody repertoires against endemic human coronaviruses in children and adults. JCI Insight 2021
Cited by: 53 | References: 70 | Related works: 10
Download PDF   Read Full Text   🔓   📖
 
Boisson‐Dupuis et al. Tuberculosis and impaired IL-23–dependent IFN-γ immunity in humans homozygous for a common TYK2 missense variant. Science Immunology 2018
Cited by: 152 | References: 99 | Related works: 10
Download PDF   Read Full Text   🔓   📖
```
<br>
<br>

### Download PDF files

Before we proceed with downloading PDF files, please read the following copyright notice:

<div style="background-color: #f0f0f0; border: 1px solid #d0d0d0; padding: 10px; margin: 10px 0;">
<strong>Copyright Notice:</strong> Downloading PDFs may be subject to copyright restrictions. Users are responsible for ensuring they have the right to access and download the content. Always respect the terms of use of the content providers and adhere to applicable copyright laws. See the following <a href="https://github.com/nicomarr/public-tutorials/blob/main/README.md">README.md</a> file for further details.
</div>

<br>
We can pass an additional argument to the `get_works()` function to save the PDF files a specified directory, like so:

{% highlight python %}
works, failed_calls = get_works(ids=uids, email=EMAIL, pdf_output_dir="./pdfs", show_progress=True)
print(f"Requests: {len(uids)}\nRetrieved: {len(works)}\nPDF files downloaded: {len([work for work in works if work['pdf_path'] is not None])}\nFailed calls: {len(failed_calls)}")
{% endhighlight %}

***Output:***
```
Retrieving works: 100%|██████████| 3/3 [00:09<00:00,  3.25s/it]
Requests: 3
Retrieved: 3
PDF files downloaded: 2
Failed calls: 0
```
<br>
<br>
The PDF files can then be used for parsing the full text, tables, and figures of the articles for retrieval augmented generation. All this will be explained in upcoming tutorials. For now, let's pay attention to the PDFs and notice that only two PDF files were successfully downloaded, even though all three articles are open access. This is because some publishers have put requirements in place that force us to use a web browser to download the PDFs. We will automate this in a later step. Let's first just inspect the output. Each element in the returned list object has the follwoing dictionary keys:

{% highlight python %}
print(works[0].keys())
{% endhighlight %}

***Output:***
```
dict_keys(['uid', 'entry_types', 'metadata', 'pdf_path', 'status_messages', 'persist_datetime'])
```
<br>
<br>
We can get status messages for each work using the 'status_messages' key.

{% highlight python %}
for work in works:
    print(f"Title: {work['metadata']['title'][:80]}...\nStatus messages: {work['status_messages']}\n")
{% endhighlight %}

***Output:***
```
Title: Harnessing large language models (LLMs) for candidate gene prioritization and se...
Status messages: 2024-08-14: Successfully retrieved metadata with UID W4387665659. 2024-08-14: PDF saved to ./pdfs/37845713_10.1186#s12967-023-04576-8_W4387665659.pdf. 

Title: Distinct antibody repertoires against endemic human coronaviruses in children an...
Status messages: 2024-08-14: Successfully retrieved metadata with UID 33497357. 2024-08-14: PDF saved to ./pdfs/33497357_10.1172#jci.insight.144499_W3125794218.pdf. 

Title: Tuberculosis and impaired IL-23–dependent IFN-γ immunity in humans homozygous fo...
Status messages: 2024-08-14: Successfully retrieved metadata with UID 10.1126/sciimmunol.aau8714. 2024-08-14: Failed to download PDF from https://immunology.sciencemag.org/content/immunology/3/30/eaau8714.full.pdf. Status code: 403. Selenium disabled. 
```
<br>
<br>
We can also get the paths to the PDFs that were downloaded by using the `pdf_path` key. Note that each PDF file is saved using the following naming convention:

`{PMID}_{DOI}_{OpenAlex ID}.pdf`

with `/` replaced by `#`. The value is `None` if the PDF file was not downloaded.

{% highlight python %}
for work in works:
    print(f"File path: {work['pdf_path']}\n")
{% endhighlight %}

***Output:***
```
File path: ./pdfs/37845713_10.1186#s12967-023-04576-8_W4387665659.pdf

File path: ./pdfs/33497357_10.1172#jci.insight.144499_W3125794218.pdf

File path: None
```
<br>
<br>
Thanks to the [Selenium Browser Automation Project](https://www.selenium.dev/), we can automate web browsers. This additional functionality requires the function to be run in a environment with the [Google Chrome Browser](https://www.google.com/chrome/) installed (e.g, in a virtual machine or on your local computer). Therefore, it will not work in the Google Colab environment.

First, let's remove any downloaded files from the previous run to give us a clean slate.

{% highlight python %}
!rm -rf ./pdfs
print("Removed pdfs directory and all its contents.")
{% endhighlight %}

***Output:***
```
Removed pdfs directory and all its contents.
```
<br>
<br>
Now, let's rerun the `get_works()` function with an additional (optional) argument, namely `enable_selenium` set to `True`. This will enable the Selenium browser automation tool to be used in the background to retrieve the full text PDFs of the works that cannot be retrieved using the `requests` library.

{% highlight python %}
works, failed_calls = get_works(uids, email=EMAIL, pdf_output_dir="./pdfs", enable_selenium=True, show_progress=True)
print(f"Requested: {len(uids)}\nRetrieved: {len(works)}\nWith PDFs: {len([work for work in works if work['pdf_path'] is not None])}")
print(f"Failed calls: {len(failed_calls)}")
{% endhighlight %}

***Output:***
```
Retrieving works: 100%|██████████| 3/3 [00:12<00:00,  4.23s/it]
Requests: 3
Retrieved: 3
PDF files downloaded: 3
Failed calls: 0
```
<br>
<br>
Some publishers require PDFs to be accessed via a browser with a visible user interface. When `enable_selenium` set to `True`, the default option is to invoke the browser to run as a background process (i.e., in headless mode). By passing in an additional (optional) argument, `is_headless=False`, we can fully automate a web browser. This will cause a web browser window to automatically open and close for each article that cannot be downloaded using the `requests` library.
<br>
<br> 
<br>

### Persist & load metadata

In addition to downloading PDF files, we can pass in an optional argument to the `get_works()`function to save the metadata to a specified directory. In doing so, the metadata for each article will be saved as a separate JSON file, using a similar naming convention as for the PDF files. The metadata can then be used later then querying an index during retrieval augmentated [text] generation. This will be the focus of a future tutorial. For now, let's run the following code to demonstrate this additional functionality:

{% highlight python %}
works, failed_calls = get_works(uids, email=EMAIL, pdf_output_dir="./pdfs", persist_dir="./cache", show_progress=True)
%ls ./cache
{% endhighlight %}

***Output:***
```
Retrieving works: 100%|██████████| 3/3 [00:09<00:00,  3.10s/it]
30578352_10.1126#sciimmunol.aau8714_W2906653622.json
33497357_10.1172#jci.insight.144499_W3125794218.json
37845713_10.1186#s12967-023-04576-8_W4387665659.json
```
<br>
<br>
Works can be loaded from storage using the `load_works_from_storage()` function, simply by providing the path to the directory where the JSON files of the works are stored. This function returns a list of works, similar to the `get_works()` function. When sorted by the `uid` (or alternatively, by using `persist_datetime` as key), we can assert that both list objects are equal.

{% highlight python %}
works_from_storage = load_works_from_storage(persist_dir="./cache")
works.sort(key=lambda x: x['uid'])
works_from_storage.sort(key=lambda x: x['uid'])
assert works == works_from_storage
{% endhighlight %}
<br>
<br>
Note that the `get_works()` function also uses the `load_works_from_storage()` function to check the cache first before making a request to the API; that is, if the storage location is specified using the `persist_dir` argument. If a work is found in the cache, it is returned directly. This speeds up the process and reduces the number of API calls made. We can illustrate this by running the get_works function again with the same uids. Before the first call, we will clear the cache directory to ensure that the works are retrieved from the API. Note the ~200x speedup when executing the function a second time.

{% highlight python %}
%rm -rf ./cache
_works, _ = get_works(uids, email=EMAIL, persist_dir="./cache", show_progress=True)
_works, _ = get_works(uids, email=EMAIL, persist_dir="./cache", show_progress=True)
%ls ./cache
{% endhighlight %}

***Output:***
```
Retrieving works: 100%|██████████| 3/3 [00:01<00:00,  2.41it/s]
Retrieving works: 100%|██████████| 3/3 [00:00<00:00, 536.10it/s]
```
<br>
<br>
To get further help on the `get_works()` function and to see all arguments available, execute `help(get_works)`.
<br>
<br>
<br>

### Get citations

Next, we want to get all articles that have cited any of the 3 articles for which we obtained the PDFs and metadata in the first place. We can do so by using the `get_citations()` function, which accepts largely the same arguments as the `get_works()` function, with two key differences:

1. We pass in the `works` object (output of the `get_works()` function) directly.
2. The process for the API call is slightly different (hence we use a separate function). This this is not important here.

The output is largely the same as for the `get_works()` function, with the difference that the value for `entry_types` is automatically set to "citing primary entry". This will allow us to differentiate between the primary articles and the articles that cite them. Moreover, the function returns single list object, not a tuple. The basic usage is as follows:

{% highlight python %}
citations = get_citations(works, email=EMAIL, show_progress=True)
{% endhighlight %}

***Output:***
```
Retrieving citations: 100%|██████████| 3/3 [00:03<00:00, 1.32s/it]
Processing citations: 100%|██████████| 216/216 [00:00<00:00, 1332308.33it/s]
```
<br>
<br>
<div style="background-color: #f0f0f0; border: 1px solid #d0d0d0; padding: 10px; margin: 10px 0;">
<strong>Reminder</strong>: When using the <strong>get_citations()</strong> function to download PDFs, please be aware of potential copyright restrictions. Ensure you have the right to access and download the content, and always respect the terms of use of the content providers. Refer to the Copyright Notice in the following <a href="https://github.com/nicomarr/public-tutorials/blob/main/README.md">README.md</a> file for more details.
</div>

<br>
To download PDFs and store the metadata in a cache directory, we can pass in the `pdf_output_dir` and `persist_dir` arguments, like so:

{% highlight python %}
citations = get_citations(works, email=EMAIL, pdf_output_dir="./pdfs", persist_dir="./cache", show_progress=True)
print(f"Citations retrieved: {len(citations)}\nPDF files downloaded: {len([work for work in citations if work['pdf_path'] is not None])}")
{% endhighlight %}

***Output:***
```
Retrieving citations: 100%|██████████| 3/3 [00:02<00:00,  1.19it/s]
Processing citations: 100%|██████████| 222/222 [00:00<00:00, 152570.13it/s]
Retrieving PDFs: 100%|██████████| 222/222 [06:00<00:00,  1.62s/it]
Persisting data: 100%|██████████| 222/222 [00:00<00:00, 624.10it/s]
Citations retrieved: 222
PDF files downloaded: 102
```
<br>
<br>
We can also enable the Selenium WebDriver and automate Chrome in headless or standard mode. This is done the same way as for the `get_works()` function.

{% highlight python %}
citations = get_citations(works, email=EMAIL, pdf_output_dir="./pdfs", persist_dir="./cache", enable_selenium=True, is_headless=False, show_progress=True)
print(f"Citations retrieved: {len(citations)}\nPDF files downloaded: {len([work for work in citations if work['pdf_path'] is not None])}")
{% endhighlight %}

***Output:***
```
Retrieving citations: 100%|██████████| 3/3 [00:02<00:00,  1.15it/s]
Processing citations: 100%|██████████| 222/222 [00:00<00:00, 545800.40it/s]
Retrieving PDFs: 100%|██████████| 222/222 [09:37<00:00,  2.60s/it]
Persisting data: 100%|██████████| 222/222 [00:00<00:00, 616.35it/s]
Citations retrieved: 222
PDF files downloaded: 151
```
<br>
<br>
The remaining citations for which the PDFs could not be downloaded have to be retrieved manually. Most of them are not open access. We will get back to this later; for now, let's get the references and related works as a next step.
<br>
<br>
<br>

### Get references and related works
Now, let's retrieve all references and related works for the three articles we obtained earlier. We'll use list comprehensions to gather this information efficiently. First, we'll collect the references for each article. References are the works cited by our original articles. We'll then flatten the resulting list of lists into a single list of reference IDs. Next, we'll gather the related works. [Related works][related-works] are identified through an algorithmic process that selects recent papers sharing the most conceptual similarities with a given paper. This selection may include preprints from bioRxiv, which might not yet be indexed in PubMed. 

{% highlight python %}
references_ids = [work['metadata']['referenced_works'] for work in works] # List comprehension
references_ids = [item for sublist in references_ids for item in sublist] # Flatten the lists
related_works_ids = [work['metadata']['related_works'] for work in works] # List comprehension
related_works_ids = [item for sublist in related_works_ids for item in sublist] # Flatten the lists
{% endhighlight %}
<br>
<br>
Now we can use the `get_works()` function in the way that allowed us to retrieve the metadata and PDF files of the 3 articles in the first place. Note the additional (optional) arguments that we pass to the `get_works()` function, as before. Specifically, we pass values for the `persist_dir` and `pdf_output_dir` arguments, which will determine if and where we save the metadata for each article and PDF files to disk. This will save us time in the future if we want to access the metadata for the works again. 

We also specify a field called `entry_type`, which indicates the type of entry we are retrieving. This field will be usefull later when we want to get information about how we retrieved the metadata for each work in the first place. This time, it is not necessary to store the output of the failed calls. Since we will pass in output from the `get_works()` function, all IDs used as input here must be valid IDs.

For now, we will retrieve the references and related works, and download PDFs with the Selenium WebDriver disabled. This can be done in Colab.

{% highlight python %}
references, _ = get_works(references_ids, email=EMAIL, pdf_output_dir="./pdfs", entry_type="reference of primary entry", show_progress=True)
related_works, _ = get_works(related_works_ids, email=EMAIL, pdf_output_dir="./pdfs", entry_type="related to primary entry", show_progress=True)
print(f"References retrieved: {len(references)}\nPDF files downloaded: {len([work for work in references if work['pdf_path'] is not None])}")
print(f"Related works retrieved: {len(related_works)}\nPDF files downloaded: {len([work for work in related_works if work['pdf_path'] is not None])}")
{% endhighlight %}
***Output:***
```
Retrieving works: 100%|██████████| 233/233 [05:31<00:00,  1.42s/it]
Retrieving works: 100%|██████████| 30/30 [00:37<00:00,  1.26s/it]
References retrieved: 233
PDF files downloaded: 74
Related works retrieved: 30
PDF files downloaded: 12
```
<br>
<br>
As described above, we can save the metedata to disk. In addition, we can set `enable_selenium=True` and `is_headless=False` to enable the Selenium WebDriver with Chrome in standard mode, which will allow us to retrieve more PDF files. This additional functionality requires the function to be run in an environment with the [Google Chrome Browser](https://www.google.com/chrome/) installed (e.g, in a virtual machine or on your local computer). Therefore, it will not work in the Colab environment. Also note that PDF files of articles which are not open access are not downloaded. 

{% highlight python %}
references, _ = get_works(references_ids, email=EMAIL, pdf_output_dir="./pdfs", persist_dir="./cache", entry_type="reference of primary entry", enable_selenium=True, is_headless=False, show_progress=True)
related_works, _ = get_works(related_works_ids, email=EMAIL, pdf_output_dir="./pdfs", persist_dir="./cache", entry_type="related to primary entry", enable_selenium=True, is_headless=False, show_progress=True)
print(f"References retrieved: {len(references)}\nPDF files downloaded: {len([work for work in references if work['pdf_path'] is not None])}")
print(f"Related works retrieved: {len(related_works)}\nPDF files downloaded: {len([work for work in related_works if work['pdf_path'] is not None])}")
{% endhighlight %}
***Output:***
```
Retrieving works: 100%|██████████| 233/233 [11:49<00:00,  3.05s/it]
Retrieving works: 100%|██████████| 30/30 [00:29<00:00,  1.03it/s]
References retrieved: 233
PDF files downloaded: 147
Related works retrieved: 30
PDF files downloaded: 12
```
<br>
<br>
Finally, we can print the total number of works retrieved, which of them are open access, and the total number of PDF files downloaded. 

{% highlight python %}
total_works = works + citations + references + related_works
print("Total number of works retrieved:", len(total_works))
print("Total number of open access works:", len([work for work in total_works if work['metadata']['open_access']['is_oa']]))
print("Total number of PDF files downloaded:", len([work for work in total_works if work['pdf_path'] is not None]))
{% endhighlight %}
***Output:***
```
Total number of works retrieved: 488
Total number of open access works: 386
Total number of PDF files downloaded: 312
```
<br>
<br>
To access the status messages of works where a PDF file could not be retrieved, we can use the following code snippet:
{% highlight python %}
for work in total_works:
    if work['pdf_path'] is None:
        print(f"Title: {work['metadata']['title'][:80]}...\nStatus messages: {work['status_messages']}\nDOI: {work['metadata']['ids'].get('doi', 'None')}\n")
{% endhighlight %}
***Output:***
```
Title: Autoimmune pathways in mice and humans are blocked by pharmacological stabilizat...
Status messages: 2024-08-14: PDF download from https://stm.sciencemag.org/content/scitransmed/11/502/eaaw1736.full.pdf using Selenium with headless mode set to False failed. 
DOI: https://doi.org/10.1126/scitranslmed.aaw1736

Title: Mendelian susceptibility to mycobacterial disease: recent discoveries...
Status messages: 2024-08-14: PDF URL not found in API call response. Skipped PDF download. 
DOI: https://doi.org/10.1007/s00439-020-02120-y

...

Title: Workflow Analysis using Graph Kernels....
Status messages: 2024-08-14: Successfully retrieved metadata with UID W2182707996. 2024-08-14: Work with UID https://openalex.org/W2182707996 is not open access or 'best_oa_location' key not found. Skipped PDF download. 
DOI: None

Title: Automating Radiologist Workflow, Part 2: Hands-Free Navigation...
Status messages: 2024-08-14: Successfully retrieved metadata with UID W2029380707. 2024-08-14: Work with UID https://openalex.org/W2029380707 is not open access or 'best_oa_location' key not found. Skipped PDF download. 
DOI: https://doi.org/10.1016/j.jacr.2008.05.012
```
<br>
<br>
Be sure to check out the accompanying [Jupyter notebook][gh-nicomarr-public-tutorials], which also includes a bonus feature to visualize open access statistics for the retrieved works.
<br>
<br>
<br>

### Wrapping up

In this tutorial, we explored using Python utility functions to interact with the OpenAlex API for retrieving full-text articles and leveraging citation data. Key points include:

1. Retrieving metadata and downloading PDF files using OpenAlex IDs, PMIDs, or DOIs.
2. Obtaining citations, references, and related works for articles.
3. Persisting metadata and automating PDF downloads with Selenium WebDriver.

We demonstrated the efficiency of this approach by automating the download of 312 PDF files out of 386 open access works, from a total of 488 works retrieved. Key takeaways:

- Subscriptions are needed for non-open access content.
- Use [Unpaywall][unpaywall-url] for open access versions of articles not automatically downloaded.
- Check the status_messages field for information on unretreived full-text content.
- Google Colab users should download data before closing sessions.
- PDF files are named using the convention: {PMID}{DOI}{OpenAlex ID}.pdf.

These utility functions provide a foundation for automating full-text article retrieval and metadata collection. Future tutorials will explore text analysis, information extraction, and integration with language models.

<br>
<br>
If you encounter any bugs in the code, have suggestions for improvements, or would like to request new features, please submit an issue at [my GitHub repo][gh-nicomarr-public-tutorials]. Your feedback is valuable for improving these tools for the research community.




[openalexR]: https://trangdata.github.io/openalexR-webinar/
[gh-nicomarr-public-tutorials]: https://github.com/nicomarr/public-tutorials
[colab-secrets]: https://x.com/GoogleColab/status/1719798406195867814
[how-to-use-the-openalex-api]: https://docs.openalex.org/how-to-use-the-api/api-overview
[related-works]: https://docs.openalex.org/api-entities/works/work-object#related_works
[ourresearch-url]: https://ourresearch.org/
[ourresearch-projects]: https://ourresearch.org/projects
[unpaywall-url]: https://unpaywall.org/products/extension
[ipython-readthedocs-magics]: https://ipython.readthedocs.io/en/stable/interactive/magics.html