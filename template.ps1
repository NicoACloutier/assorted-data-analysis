#This script takes a single parameter, the name of a directory, and creates an empty file structure for a data science project
#in that directory. My earlier projects were made without a common template, so they will not abide by this structure, and later 
#projects may potentially stray from it in one way or another. Over time, I may add more or change this basic template, but for 
#now this is what I will use to structure my projects.

param($dir)

mkdir .\$dir
cd .\$dir

New-Item -Name RESULTS.ipynb -ItemType File
Set-Content .\RESULTS.ipynb '
{
 "cells": [],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 2
}'

mkdir .\data
cd .\data

mkdir .\raw
mkdir .\cleaned
mkdir .\for_model
cd ..

mkdir .\preprocessing

mkdir .\model
cd .\model

mkdir .\saves
cd ..

mkdir .\database
cd ..

cd ..