# Parser_txt2stat
[2022-10] a parser for meteorological txt data to get stat (mean, stabdard variation, min, max). Use it in CLI with some args.


# Configuration 
In config/config.json
```
{
  "HTTP_SOURCE": "https://static.meteo-paris.com/station/downld02.txt",
  "OUT_DIRECTORY": "download",
  "OUT_DEFAULT_FILE_NAME": "default",
  "OUT_DEFAULT_FILE_EXTENSION": ".txt",
  "RELATIVE_OUT_PATH": "."
}
```
# CLI parameters

* -h or --help : show help 
* -f or --file : work with this file instead of download the file from source set in the config
* -fp or --filepath : FileType(encoding='utf8') work with this file instead of download the file from source set in the config
* -m or --metrics, nargs=*, choices between min (minimum), max (maximum), stddev(standard deviation) : list the type of stats you need on the columns (default)
* -c or --columns, nargs=+, type=int : list the indexes of the columns you want to treat in the file
