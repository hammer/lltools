CREATE TABLE vocabulary ( italian text, english text, pronunciation text, part_of_speech text, gender text );
COPY vocabulary FROM '' WITH DELIMITER '|';
