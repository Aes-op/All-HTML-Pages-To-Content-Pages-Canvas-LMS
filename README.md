# All-HTML-Pages-To-Content-Pages-Canvas-LMS

This script is used to create content pages from HTML files in a Canvas course. It will replace any linked HTML pages with the equivalent created content page. It will also delete any HTML files converted during its runtime.

WARNINGS:
There are required non-standard python modules for these scripts that are imported in the script. This script will not run without them.

This script is provided as is and there is no guarantee of it working correctly with Canvas as updates are released. Always test it on a test version of your Canvas instance to make sure that the script still functions correctly.


The flow this script is as follows:

1. All linked HTML pages in the Canvas course are converted to content pages
2. All linked HTML pages are replaced in the course with the equivalent content pages
3. All previously linked and replaced HTML pages are deleted from the Canvas course (as long as there were less than 25 HTML files deleted over the course of this script; they can be recovered through the file restoration in Canvas.)
4. All non-linked HTML pages in the course are converted to content pages
5. All non-linked HTML pages are deleted

NOTE: The functions in this script can be easily broken out into separate scripts to allow for only linked, or only unlinked, HTML pages to be converted.
