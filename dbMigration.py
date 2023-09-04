import asyncio
import json
from typing import List, Optional

from storage.backingPsqlDatabase import BackingPsqlDatabase
from storage.psqlCredentialsProvider import PsqlCredentialsProvider

print(f'starting...')

eventLoop = asyncio.get_event_loop()
psqlCredentialsProvider = PsqlCredentialsProvider('storage/psqlCredentials.json')
backingPsqlDatabase = BackingPsqlDatabase(
    eventLoop = eventLoop,
    psqlCredentialsProvider = psqlCredentialsProvider
)

print(f'finished creating dependencies...')

async def main():
    connection = await backingPsqlDatabase.getConnection()
    records = await connection.fetchRows(
        '''
            SELECT additionalanswers, triviaid, triviasource, triviatype, userid FROM old_additionaltriviaanswers
        '''
    )

    if records is not None and len(records) >= 1:
        for index, record in enumerate(records):
            print(f'Updating record #{index}...')

            rawJsonString: Optional[str] = record[0]
            triviaId: Optional[str] = record[1]
            triviaSource: Optional[str] = record[2]
            triviaType: Optional[str] = record[3]
            userId: Optional[str] = record[4]

            if not isinstance(rawJsonString, str) or len(rawJsonString) == 0 or rawJsonString.isspace():
                continue
            elif not isinstance(triviaId, str) or len(triviaId) == 0 or triviaId.isspace():
                continue
            elif not isinstance(triviaSource, str) or len(triviaSource) == 0 or triviaSource.isspace():
                continue

            jsonArray: Optional[List[Optional[str]]] = json.loads(rawJsonString)

            if jsonArray is None or len(jsonArray) == 0:
                continue

            for answerString in jsonArray:
                if answerString is None or len(answerString) == 0 or answerString.isspace():
                    continue

                await connection.execute(
                    '''
                        INSERT INTO additionaltriviaanswers (additionalanswer, triviaid, triviasource, triviatype, userid)
                        VALUES ($1, $2, $3, $4, $5)
                    ''',
                    answerString, triviaId, triviaSource, triviaType, userId
                )

            print(f'Finished record #{index}')

    await connection.close()

eventLoop.run_until_complete(main())
