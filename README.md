Your tv episodes collection is upside down ? 
This python tool aim to clean all your messy collection by giving each episode a pretty name and a coherent location.
The subtitles are also managed !

#Features
 * Rename & Move files to organized directories
 * Look online for episode name & number of episodes
 * Find and renames subtitles

#Instructions
    ./shorganizer.py  --in=dir --in=other_dir --out=destination_dir
      --list #list all episodes found
      --relocate #move episodes and subtitles to the destination directory
      --debug #display more log
      --pattern #renamming pattern, must be a python formating string. valides keys are : show, season,  episode, episode_name and episode_str(SXXEXX)

#TODO
 * Download missing subtitles
 * Manages languages for subtitles and shows/episodes names
 * Export statistics for missings episodes, incompletes series
 * Deals with duplicates and differents qualities & format (HD, LD)
 * A pretty UI would be...pretty, right ?
 * Manage movies & movies subtitles
 
 