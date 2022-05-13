# https://github.com/casey/just
pipcompile reqfiles='requirements*.in':
    @for reqfile in `ls {{ reqfiles }}`; do \
        echo "pip-compile -q $reqfile"; \
        pip-compile -q $reqfile; \
    done

pipsync:
    pip-sync requirements.txt requirements_dev.txt

test:
    python manage.py test

precommit:
    pre-commit run --all-files
