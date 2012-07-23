#Manage your digital tv shows collection with Shorganizer !

Your tv episodes collection is upside down ? 
This python tool aim to clean all your messy collection by giving each episode a pretty name and a coherent location.

##Features
 * Rename & Move episodes files (video & subtitles) to organized directories
 * Look online for episodes name and more using [BetaSeries](http://betaseries.com)

##Instructions
###Options
`./shorganizer.py  --in=dir --in=other_dir --out=destination_dir`

   `--list` list all episodes found

   `--relocate` move episodes and subtitles to the destination directory
   
   `--debug` display more log
   
   `--missing` display missing episodes
   
   `--pattern` renamming pattern, must be a python formating string. valides keys are : show, season,  episode, episode_name and episode_str (SXXEXX)     

###Custom names
You can modify the `shows` file in the sources directory to help detect shows wrongly named.
The left part of a line is the name on your disk, the second should match the name on betaseries

##TODO
 * Download missing subtitles
 * Manages languages for subtitles and shows/episodes names
 * Export statistics for missings episodes, incompletes series
 * Deals with duplicates and differents qualities & format (HD, LD)
 * A pretty UI would be...pretty, right ?
 * Manage movies & movies subtitles
 
 