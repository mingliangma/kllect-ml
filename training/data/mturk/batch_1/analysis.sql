/****** Script for SelectTopNRows command from SSMS  ******/
DECLARE @BATCH_ID int;
SET @BATCH_ID = 2;

/** GET invalid video ids. Need re-labelling **/
/*SELECT  distinct video_id
  FROM [dbo].[INPUT_DATA] B
  WHERE batch_id = @BATCH_ID AND question_id = 0 AND video_id NOT IN (
  SELECT video_id 
  FROM [dbo].[SAMPLE_LABELS] A
  WHERE A.batch_id = B.batch_id AND A.batch_id = @BATCH_ID
  )

/** Get valid HITs **/

SELECT  distinct hit_id
  FROM [dbo].[INPUT_DATA] B
  INNER JOIN dbo.HITS C
  ON B.input_id = C.input_id
  WHERE B.batch_id = C.batch_id
  AND B.batch_id = @BATCH_ID AND question_id = 0 AND video_id IN (
  SELECT video_id 
  FROM [dbo].[SAMPLE_LABELS] A
  WHERE A.batch_id = B.batch_id  AND A.batch_id = @BATCH_ID
  )*/



/** Get "qualified assignments: assignments with the same answer as the labelled data **/
SELECT correct_assignments, count(distinct hit_id) as hits
FROM (
SELECT hit_id, count(assignment_id) as correct_assignments
FROM
(SELECT 
  A.batch_id, C.hit_id, A.video_id, A.label, B.question_id, assignment_id
  FROM [dbo].[SAMPLE_LABELS] A
  INNER JOIN [dbo].[INPUT_DATA] B
  ON A.batch_id = B.batch_id AND A.video_id = B.video_id --AND A.batch_id = 3
  INNER JOIN [dbo].[HITS] C
  ON B.batch_id = C.batch_id AND B.input_id = C.input_id
  LEFT OUTER JOIN [dbo].[HIT_RESULTS] D
  ON C.hit_id = D.hit_id AND B.question_id = D.question_id AND A.label = D.label
  ) R
  group by hit_id) R1
  group by correct_assignments
  order by correct_assignments

SELECT *
FROM [dbo].[HIT_RESULTS] A 
INNER JOIN [dbo].[HITS] B
ON A.batch_id = B.batch_id AND A.hit_id = B.hit_id
INNER JOIN [dbo].[INPUT_DATA] C
ON B.batch_id = C.batch_id AND B.input_id = C.input_id
INNER JOIN [dbo].[SAMPLE_LABELS] D
ON C.batch_id = D.batch_id AND C.video_id = D.video_id
WHERE A.question_id = 0 --AND A.batch_id = 3
ORDER BY A.hit_id, A.assignment_id


SELECT count(distinct hit_id)
FROM
(SELECT A.label, A.hit_id, count(distinct assignment_id) as cnt
FROM [dbo].[HIT_RESULTS] A 
INNER JOIN [dbo].[HITS] B
ON A.batch_id = B.batch_id AND A.hit_id = B.hit_id
INNER JOIN [dbo].[INPUT_DATA] C
ON B.batch_id = C.batch_id AND B.input_id = C.input_id
AND A.question_id = C.question_id
INNER JOIN [dbo].[SAMPLE_LABELS] D
ON C.batch_id = D.batch_id AND C.video_id = D.video_id
WHERE A.question_id = 0 --AND A.batch_id = 3 
AND A.hit_id in (
SELECT 
  distinct C.hit_id
  FROM [dbo].[SAMPLE_LABELS] A
  INNER JOIN [dbo].[INPUT_DATA] B
  ON A.batch_id = B.batch_id AND A.video_id = B.video_id --AND A.batch_id = 3
  INNER JOIN [dbo].[HITS] C
  ON B.batch_id = C.batch_id AND B.input_id = C.input_id
  LEFT OUTER JOIN [dbo].[HIT_RESULTS] D
  ON C.hit_id = D.hit_id AND B.question_id = D.question_id AND A.label = D.label AND B.question_id = 0
  GROUP BY C.hit_id, A.video_id
  HAVING count(assignment_id) < 2)
--AND A.hit_id = '3BAKUKE49HCUVQ3EPJ279X4X9BER1X'
GROUP BY A.label, A.hit_id
HAVING count(distinct assignment_id) > 1) R


  /** Populate the qualified results table **/
TRUNCATE TABLE[dbo].[HIT_QUALIFITED_RESULTS]
INSERT INTO [dbo].[HIT_QUALIFITED_RESULTS](
  batch_id, hit_id, assignment_id, worker_id)

SELECT batch_id, hit_id, assignment_id, worker_id
FROM ((
SELECT D.batch_id, C.hit_id, assignment_id, worker_id
  FROM [dbo].[SAMPLE_LABELS] A
  INNER JOIN [dbo].[INPUT_DATA] B
  ON A.batch_id = B.batch_id AND A.video_id = B.video_id --AND A.batch_id = 1
  INNER JOIN [dbo].[HITS] C
  ON B.batch_id = C.batch_id AND B.input_id = C.input_id
  INNER JOIN [dbo].[HIT_RESULTS] D
  ON C.hit_id = D.hit_id AND B.question_id = D.question_id AND A.label = D.label
  )
UNION
(
SELECT R2.batch_id, R2.hit_id, R2.assignment_id, R2.worker_id
FROM
(SELECT A.batch_id, A.question_id, A.label, A.hit_id
FROM [dbo].[HIT_RESULTS] A 
INNER JOIN [dbo].[HITS] B
ON A.batch_id = B.batch_id AND A.hit_id = B.hit_id
INNER JOIN [dbo].[INPUT_DATA] C
ON B.batch_id = C.batch_id AND B.input_id = C.input_id
AND A.question_id = C.question_id
INNER JOIN [dbo].[SAMPLE_LABELS] D
ON C.batch_id = D.batch_id AND C.video_id = D.video_id
WHERE A.question_id = 0 --AND A.batch_id = 3 
AND A.hit_id in (
SELECT 
  distinct C.hit_id
  FROM [dbo].[SAMPLE_LABELS] A
  INNER JOIN [dbo].[INPUT_DATA] B
  ON A.batch_id = B.batch_id AND A.video_id = B.video_id --AND A.batch_id = 1
  INNER JOIN [dbo].[HITS] C
  ON B.batch_id = C.batch_id AND B.input_id = C.input_id
  LEFT OUTER JOIN [dbo].[HIT_RESULTS] D
  ON C.hit_id = D.hit_id AND B.question_id = D.question_id AND A.label = D.label AND B.question_id = 0
  GROUP BY C.hit_id, A.video_id
  HAVING count(assignment_id) < 2)
--AND A.hit_id = '3BAKUKE49HCUVQ3EPJ279X4X9BER1X'
GROUP BY A.batch_id,A.question_id,  A.label, A.hit_id
HAVING count(distinct assignment_id) > 1) R1
INNER JOIN [dbo].[HIT_RESULTS] R2
ON R1.batch_id = R2.batch_id AND R1.hit_id = R2.hit_id
AND R1.question_id = R2.question_id AND R1.label = R2.label)
  ) R


SELECT distinct A.batch_id, A.hit_id, A.question_id, description_YN
FROM [dbo].[HIT_RESULTS] A
INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
--AND A.batch_id = 3
where A.question_id > 0
group by A.batch_id, A.hit_id, A.question_id, description_YN
having count(distinct A.assignment_id) >= 2

/** Get number of videos receiving agreement among at least two worker for the descriptionType question **/
--SELECT distinct A.batch_id, A.hit_id, A.question_id
select description_YN, count(distinct video_id) as cnt
FROM 
(SELECT distinct A.batch_id, A.hit_id, A.question_id, description_YN
FROM [dbo].[HIT_RESULTS] A
INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
AND A.batch_id = 3
INNER JOIN [dbo].[HITS] C
ON A.batch_id = C.batch_id AND A.hit_id = C.hit_id
where A.question_id > 0
group by A.batch_id, A.hit_id, A.question_id, description_YN
having count(distinct A.assignment_id) >= 2
) R1
INNER JOIN [dbo].[INPUT_DATA] R2
ON R1.batch_id = R2.batch_id AND R1.question_id = R2.question_id
group by description_YN


select description_YN, count(video_id)
FROM 
(SELECT distinct A.batch_id, A.hit_id, A.question_id, C.input_id, description_YN
FROM [dbo].[HIT_RESULTS] A
INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
AND A.batch_id = 3
INNER JOIN [dbo].[HITS] C
ON A.batch_id = C.batch_id AND A.hit_id = C.hit_id
where A.question_id > 0
group by A.batch_id, A.hit_id, A.question_id, C.input_id, description_YN
having count(distinct A.assignment_id) >= 2
) R1
INNER JOIN [dbo].[INPUT_DATA] R2
ON R1.batch_id = R2.batch_id AND R1.question_id = R2.question_id
AND R1.input_id = R2.input_id
GROUP BY description_YN

/** Get number of videos receiving inconsistent answers among at least two worker for the descriptionType question **/
select R1.batch_id, R1.hit_id, R1.question_id, R1.description_YN, count(*)
FROM [dbo].[HIT_RESULTS] R1
INNER JOIN

(
SELECT batch_id, hit_id, question_id, COUNT(description_YN) as distinct_answers
FROM
(SELECT A.batch_id, A.hit_id, A.question_id, description_YN,
count(distinct A.assignment_id) as description_answers
FROM [dbo].[HIT_RESULTS] A
INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
 AND A.batch_id = 3
where question_id > 0
group by A.batch_id, A.hit_id, A.question_id, description_YN
having count(distinct A.assignment_id) >= 2) R
GROUP BY  batch_id, hit_id, question_id
HAVING COUNT(description_YN) > 1) R2
ON R1.batch_id = R2.batch_id AND R1.hit_id = R2.hit_id AND R1.question_id = R2.question_id 
group by  R1.batch_id, R1.hit_id, R1.question_id, R1.description_YN



/** Get number of videos receiving agreement among at least two worker for the sub category question **/
select count(distinct video_id)
from (
SELECT distinct A.batch_id, A.hit_id, A.question_id, C.input_id
FROM [dbo].[HIT_RESULTS] A
INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
 AND A.batch_id = 3
INNER JOIN [dbo].[HITS] C
ON A.batch_id = C.batch_id AND A.hit_id = C.hit_id
where A.question_id > 0
group by A.batch_id, A.hit_id, A.question_id, C.input_id, label
having count(distinct A.assignment_id) >= 2
--ORDER BY batch_id, hit_id, question_id 
) R1
INNER JOIN [dbo].[INPUT_DATA] R2
ON R1.batch_id = R2.batch_id AND R1.question_id = R2.question_id
AND R1.input_id = R2.input_id


select label, count(*) as cnt
from (
SELECT distinct A.batch_id, A.hit_id, A.question_id, label, count(distinct A.assignment_id) AS agreements
FROM [dbo].[HIT_RESULTS] A
INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
 AND A.batch_id = 3
where question_id > 0
group by A.batch_id, A.hit_id, A.question_id, label
having count(distinct A.assignment_id) >= 2
--ORDER BY batch_id, hit_id, question_id 
) R
group by label
order by cnt desc, label


/** Populate selected reliable MTurk labels **/
INSERT INTO [dbo].[MTURK_SELECTED_DESCRIPTION_YN]
(batch_id, video_id, description_YN)
SELECT distinct H.batch_id, video_id, description_YN
FROM
(
SELECT distinct *
	FROM (
			SELECT A.batch_id, A.hit_id, A.question_id, description_YN
			FROM [dbo].[HIT_RESULTS] A
			INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
			ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
			 AND A.batch_id = 3
			where A.question_id > 0
			group by A.batch_id, A.hit_id, A.question_id, description_YN
			having count(distinct A.assignment_id) >= 2
	) R1
	WHERE NOT EXISTS
	(
		SELECT batch_id, hit_id, question_id
		FROM
		(
			SELECT A.batch_id, A.hit_id, A.question_id, description_YN,
			count(distinct A.assignment_id) as description_answers
			FROM [dbo].[HIT_RESULTS] A
			INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
			ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
			 AND A.batch_id = 3
			where question_id > 0
			group by A.batch_id, A.hit_id, A.question_id, description_YN
			having count(distinct A.assignment_id) >= 2
		) R
		WHERE R.batch_id = R1.batch_id AND R1.hit_id = R.hit_id AND R.question_id = R1.question_id
		GROUP BY  batch_id, hit_id, question_id
		HAVING COUNT(description_YN) > 1
	)
) SELECTED_LABELS
INNER JOIN [dbo].[HITS] H
ON SELECTED_LABELS.batch_id = H.batch_id AND SELECTED_LABELS.hit_id = H.hit_id
INNER JOIN [dbo].[INPUT_DATA] D
ON SELECTED_LABELS.batch_id = D.batch_id AND SELECTED_LABELS.question_id = D.question_id AND H.input_id = D.input_id


DELETE FROM [dbo].[MTURK_SELECTED_LABELS] --WHERE batch_id = 3
INSERT INTO [dbo].[MTURK_SELECTED_LABELS]
(batch_id, video_id, category, label)
SELECT distinct H.batch_id, video_id, 'Technology' as category, label
FROM
(
	SELECT distinct A.batch_id, A.hit_id, A.question_id, label
	FROM [dbo].[HIT_RESULTS] A
	INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
	ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
	 --AND A.batch_id = 3
	where question_id > 0
	group by A.batch_id, A.hit_id, A.question_id, label
	having count(distinct A.assignment_id) >= 2
) SELECTED_LABELS
INNER JOIN [dbo].[HITS] H
ON SELECTED_LABELS.batch_id = H.batch_id AND SELECTED_LABELS.hit_id = H.hit_id
INNER JOIN [dbo].[INPUT_DATA] D
ON SELECTED_LABELS.batch_id = D.batch_id AND SELECTED_LABELS.question_id = D.question_id AND H.input_id = D.input_id
where datalength(label) > 0

/** Relaxed version **/
INSERT INTO [dbo].[MTURK_SELECTED_LABELS_RELAXED]
(batch_id, video_id, category, label)
SELECT distinct H.batch_id, video_id, 'Technology' as category, label
FROM
((
	SELECT distinct A.batch_id, A.hit_id, A.question_id, label
	FROM [dbo].[HIT_RESULTS] A
	INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
	ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
	 --AND A.batch_id = 3
	where question_id > 0
	group by A.batch_id, A.hit_id, A.question_id, label
	having count(distinct A.assignment_id) > 1
) UNION
(
  SELECT distinct A.batch_id, A.hit_id, A.question_id, label
	FROM [dbo].[HIT_RESULTS] A
	INNER JOIN [dbo].[HIT_QUALIFITED_RESULTS] B
	ON A.batch_id = B.batch_id and A.hit_id = B.hit_id AND A.assignment_id = B.assignment_id and A.worker_id = B.worker_id
	 --AND A.batch_id = 3
	where question_id > 0 AND label in (SELECT label from [dbo].[PREDEFINED_LABELS] WHERE category =  'Technology')
)
)SELECTED_LABELS
INNER JOIN [dbo].[HITS] H
ON SELECTED_LABELS.batch_id = H.batch_id AND SELECTED_LABELS.hit_id = H.hit_id
INNER JOIN [dbo].[INPUT_DATA] D
ON SELECTED_LABELS.batch_id = D.batch_id AND SELECTED_LABELS.question_id = D.question_id AND H.input_id = D.input_id
where datalength(label) > 0 AND datalength(label) < 100
