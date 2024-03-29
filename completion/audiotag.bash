#TODO: lint and redo this
_audiotag_completions()
{
	compopt +o default
	COMP_WORDBREAKS=${COMP_WORDBREAKS//=}
	local cur=${COMP_WORDS[COMP_CWORD]}
	local lastcommand=$(_audiotag_lastcommand)
	local commands=(print interactive set clean copy rename -v -h --version --help)
	local rename_commands=(--pattern= --force -f)
	local clean_commands=(--keep= -k)
	local interactive_commands=(--compilation -c)
	local set_commands=(--noartist --noalbumartist --notitle --noalbum --nodate\
		--nogenre --notracknumber --notracktotal --nodiscnumber --nodisctotal\
		--artist= --albumartist= --title= --album= --date= --genre= --tracknumber=\
		--tracktotal= --discnumber= --disctotal=)

	if [[ ${COMP_CWORD} == 1 ]]; then
		COMPREPLY=($(compgen -W "${commands[*]}" -- ${cur}))
	else
		case ${lastcommand} in
			print)
				compopt -o default
				COMPREPLY=()
				;;
			copy)
				compopt -o dirnames
				COMPREPLY=()
				;;
      clean)
				if [[ ${cur} == -* ]]; then
					if [[ ${cur} == --p* ]]; then
						compopt -o nospace
					fi
					COMPREPLY=($(compgen -W "${clean_commands[*]}" -- ${cur}))
				else
					compopt -o default
					COMPREPLY=()
				fi
				;;
      interactive)
				if [[ ${cur} == -* ]]; then
					COMPREPLY=($(compgen -W "${interactive_commands[*]}" -- ${cur}))
				else
					compopt -o default
					COMPREPLY=()
				fi
				;;
			rename)
				if [[ ${cur} == -* ]]; then
					if [[ ${cur} == --p* ]]; then
						compopt -o nospace
					fi
					COMPREPLY=($(compgen -W "${rename_commands[*]}" -- ${cur}))
				else
					compopt -o default
					COMPREPLY=()
				fi
				;;
			set)
				if [[ ${cur} == -* ]]; then
					if [[ ${cur} != --no* ]]; then
						compopt -o nospace
					fi
					COMPREPLY=($(compgen -W "${set_commands[*]}" -- ${cur}))
				else
					compopt -o default
					COMPREPLY=()
				fi
				;;
		esac
	fi
}

_audiotag_lastcommand()
{
	local firstword i

	firstword=
	for ((i = 1; i < ${#COMP_WORDS[@]}; ++i)); do
		if [[ ${COMP_WORDS[i]} != -* ]]; then
			firstword=${COMP_WORDS[i]}
			break
		fi
	done

	echo $firstword
}

complete -F _audiotag_completions audiotag
