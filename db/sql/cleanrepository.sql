delete from repository where length(description)<5;

delete from repository where description like '%my first%' ;

delete from repository  where length(description) < 30 and description like '%test%';

delete from repository where description like '%first%' and length(description) < 50;

delete from repository where name like '%first%' ;

delete from repository where name like '%demo%';

delete from repository where name like '%sample%' and length(description) <50 ;

delete from repository where description like '%sample app%' and length(description) <50 ;

delete from repository where  length(description) <30 ;

