# Shamrock Gardens Elementary Agenda Generator

This script allows you to generate a pdf of the agenda calendar for a
calendar year.

## To run the script:

1. Fill out the excel sheet with events using calendar.xlsx as a template.
2. The repository contains a file called `default.nix` that will help
   you create a Python environment specifically for this script (See the
   Nix-shell explanation below.)
3. Run the script filling in a first date, last date, and source
   calendar file. For example, to generate a calendar starting on August
   5, 2021 and ending on June 6, 2022 the command would look like: `$ python generate_calendar.py --first 08/05/2021 --last 06/06/2022
   --source calendar.xlsx`
4. The output will be saved to `agenda_out.pdf`


### Nix-shell on MacOs:

This approach provides a fully isolated environment that allows you to run the application
without worrying about any dependency collisions. This approach also provides some system
packages automatically.

```
Install and setup nix:
    $ curl -L https://nixos.org/nix/install | sh
    $ nix-env -i direnv

    # Add direnv hook call to your shell profile
    # For example in zsh:
    $ echo "eval \"\$(direnv hook zsh)\"" >> .zshrc
    $ source .zshrc

    $ cd path/to/your/repository/
    $ direnv allow .
    You may need to `cd` out of the directory and back after running this command

Install dependencies (requires nix setup):
    $ cd path/to/your/repository/
    $ pip install -r requirements.txt
```
