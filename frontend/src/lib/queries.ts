import { useQuery } from 'react-query';
import { getCrews, getCrewById } from './api';

export const useCrews = () => {
  return useQuery('crews', () => getCrews().then(res => res.data));
};

export const useCrew = (crewId: string) => {
  return useQuery(['crew', crewId], () => getCrewById(crewId).then(res => res.data), {
    enabled: !!crewId
  });
};
